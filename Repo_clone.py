# cloning the phonepe pulse repository
import git
repo_url = "https://github.com/PhonePe/pulse.git"

destination = "E:\GUVI - DS\Phonepe_pulse\data"

from git import Repo

Repo.clone_from(repo_url, destination)

