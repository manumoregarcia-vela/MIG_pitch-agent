import argparse

from pipeline.run_pipeline import run


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MIG pitch pipeline entrypoint")
    parser.add_argument("--mode", choices=["json", "document"], default="document")
    parser.add_argument("--input", default=None)
    parser.add_argument("--data-dir", default="data")
    args = parser.parse_args()

    run(mode=args.mode, input_path=args.input, data_dir=args.data_dir)
