"""coursesmith: sourced courses from Wikipedia and other vetted sources, ordered foundational to advanced."""
import warnings

# urllib3 v2 warns on macOS's LibreSSL-built Python; harmless here.
warnings.filterwarnings("ignore", message=".*OpenSSL.*")

__version__ = "0.2.0"
