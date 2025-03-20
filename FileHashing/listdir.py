import asyncio
from pathlib import Path
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import logging
import argparse

BATCH_SIZE = 20
EXCLUDED_DIRS = {'$RECYCLE.BIN', 'System Volume Information'}
HASH_ALGORITHM = 'blake2b'
CHUNK_SIZE = 8388608  # 8 MB

# ✅ Separate flags for object-level and batch-level handling
first_entry_written = False
first_batch_written = False


def setup_logging(logfile):
    """Configure logging to file or console."""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    handler = logging.FileHandler(logfile) if logfile else logging.StreamHandler()
    
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    
    # ✅ Remove any existing handlers to avoid duplicates
    if logger.hasHandlers():
        logger.handlers.clear()
    
    logger.addHandler(handler)


def compute_file_hash(file_path):
    """Computes the hash using a faster hashing algorithm (blake2b) in chunks."""
    hash_func = hashlib.new(HASH_ALGORITHM)
    try:
        with open(file_path, 'rb') as f:
            while chunk := f.read(CHUNK_SIZE):
                hash_func.update(chunk)
        return hash_func.hexdigest()
    except Exception as e:
        logging.warning(f"Failed to compute hash for {file_path}: {e}")
        return None


async def list_files_in_batches(root_dir):
    file_batch = []
    try:
        for file in Path(root_dir).rglob('*'):
            if any(part in EXCLUDED_DIRS for part in file.parts):
                continue

            if file.is_file():
                file_batch.append(file)
                if len(file_batch) == BATCH_SIZE:
                    yield file_batch
                    file_batch = []

        if file_batch:
            yield file_batch

    except PermissionError as e:
        logging.warning(f"Permission denied: {e}")
    except Exception as e:
        logging.error(f"Error while listing files: {e}")


async def process_batch(batch):
    results = []

    with ProcessPoolExecutor() as hash_executor:
        # ✅ Compute hashes in parallel using ProcessPoolExecutor
        hash_futures = [
            asyncio.get_event_loop().run_in_executor(hash_executor, compute_file_hash, file)
            for file in batch
        ]
        computed_hashes = await asyncio.gather(*hash_futures)

        # ✅ Combine results
        for file, file_hash in zip(batch, computed_hashes):
            if file_hash:
                result = {'file_path': str(file), 'hash': file_hash}
                logging.info(json.dumps(result, indent=4))
                results.append(result)

    return results


async def write_to_json(data, output_file, is_last_batch):
    global first_entry_written, first_batch_written

    if data:
        try:
            with open(output_file, 'a') as f:
                # ✅ Write opening bracket if this is the first batch
                if not first_batch_written:
                    f.write('{\n  "hashes": [\n')
                    first_batch_written = True

                for index, entry in enumerate(data):
                    # ✅ Insert comma ONLY if this is NOT the first object in the entire file
                    if first_entry_written:
                        f.write(',\n')

                    # ✅ Write the JSON object
                    json.dump(entry, f, indent=4)

                    # ✅ Mark that an entry has been written (now it's safe to add a comma next time)
                    first_entry_written = True

                # ✅ If this is the last batch, close the JSON array and object properly
                if is_last_batch:
                    f.write('\n  ]\n}\n')

        except Exception as e:
            logging.error(f"Error writing to JSON file: {e}")


async def main(root_dir, output_file, dry_run):
    global first_entry_written, first_batch_written
    is_last_batch = False

    # ✅ Truncate the file if it already exists
    open(output_file, 'w').close()

    async for batch in list_files_in_batches(root_dir):
        logging.info(f"Processing batch of {len(batch)} files...")

        # ✅ Make sure all hashes are computed before writing
        results = await process_batch(batch)

        # ✅ Determine if this is the last batch
        is_last_batch = len(batch) < BATCH_SIZE

        if not dry_run and results:
            await write_to_json(results, output_file, is_last_batch)

        logging.info('-' * 40)

    # ✅ Ensure the JSON is properly closed if it wasn't closed in the last batch
    if not dry_run and not is_last_batch:
        with open(output_file, 'a') as f:
            f.write('\n  ]\n}\n')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate file hashes and store them in a JSON file.")
    parser.add_argument('--root-dir', type=str, required=True, help='Root directory to scan')
    parser.add_argument('--output', type=str, required=True, help='Output JSON file path')
    parser.add_argument('--dry-run', action='store_true', help="Simulate the process without writing to a file")
    parser.add_argument('--logfile', type=str, help="Optional log file path (if omitted, logs are printed to console)")

    args = parser.parse_args()

    # ✅ Setup logging based on --logfile parameter
    setup_logging(args.logfile)

    asyncio.run(main(args.root_dir, args.output, args.dry_run))
