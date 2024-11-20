from fastapi.templating import Jinja2Templates
from pathlib import Path

root_dir = Path(__file__).resolve().parent
template_dir = root_dir / "templates"


jinja = Jinja2Templates(directory=str(template_dir))
