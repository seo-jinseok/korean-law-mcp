from .server import mcp
# Import modules to register tools, resources, and prompts
from . import tools
from . import resources
from . import prompts
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("korean-law-mcp")

def main():
    mcp.run()

if __name__ == "__main__":
    main()
