
from PyQt5 import uic

with open("okul_zili_UI.py", "w", encoding='utf-8') as fout:
    uic.compileUi('okul_zili.ui', fout)
