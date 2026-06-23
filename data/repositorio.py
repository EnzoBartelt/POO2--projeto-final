import json
import sys
from pathlib import Path

from models.avaliacao import Avaliacao
from models.midia import Midia, Filme, Serie
from models.usuario import Usuario


class Repositorio:
    _default_path = Path(".repositorio")

    def __init__(self):
        if not self._default_path.exists():
            self._default_path.mkdir()
        elif not self._default_path.is_dir():
            raise Exception(f"Arquivo '{str(self._default_path)}' não é um diretório")

        # refatorar depois
        self._midias: dict[int, Midia] = {}
        path = self._default_path / "midias.json"
        if not path.exists():
            path.write_text("{}")
        else:
            for key, val in json.loads(path.read_text(encoding="utf-8")).items():
                if val["media_type"] == "movie":
                    self._midias[key] = Filme()
                elif val["media_type"] == "tv":
                    self._midias[key] = Serie()
                else:
                    print(
                        f"Mídia de ID {val['id']} possui tipo desconhecido '{val['media_type']}', ignorando entrada",
                        file=sys.stderr,
                    )

        self._usuarios = []
        path = self._default_path / "usuarios.json"
        if not path.exists():
            path.write_text("{}")
        else:
            for key, val in json.loads(path.read_text(encoding="utf-8")).items():
                filmes: dict[Midia, Avaliacao] = {
                    self.midias[id]: Avaliacao() for id, aval in val["filmes"].items()
                }
                self._usuarios.append(
                    Usuario(val["nome"], val["email"], val["hash_senha"], filmes)
                )
