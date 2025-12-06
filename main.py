import json
import sys

from Vionix.pipeline import LanguagePipeline
from Vionix.utils import VionixError, get_logger

logger = get_logger()

def load_config(path="app_config.json"):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except VionixError:
        logger.error(f"Config file not found at {path}")
        raise VionixError(f"Config file not found at {path}")
    except Exception as e:
        logger.exception("Failed to load config")
        raise VionixError(f"Failed to load config: {e}") from e

def main():
    try:
        cfg = load_config()
        text = cfg.get("test_text") or "This is a Vionix cinematic pipeline test."
        pipeline = LanguagePipeline(cfg)
        out = pipeline.run(text)
        print("\n✅ Final video created at:", out)
        logger.info(f"Final output: {out}")
    except VionixError as e:
        logger.error("Pipeline terminated: " + str(e))
        print("\n❌ Pipeline terminated. Check logs.")
        sys.exit(1)
    except Exception as e:
        logger.exception("Unhandled error in main")
        print("\n❌ Unexpected failure. Check logs.")
        sys.exit(1)

if __name__ == "__main__":
    main()
