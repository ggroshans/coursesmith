"""wikicourse: Wikipedia subjects as sourced courses, ordered foundational to advanced."""
import warnings

# urllib3 v2 warns on macOS's LibreSSL-built Python; harmless here.
warnings.filterwarnings("ignore", message=".*OpenSSL.*")

__version__ = "0.1.0"
