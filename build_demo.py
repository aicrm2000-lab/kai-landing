# -*- coding: utf-8 -*-
"""Сборка фрагмента демо «напиши — CRM собирается» в блоке «Как работает».

Вход: demo_data.json. Выход: разметка между <!-- KD:START --> и <!-- KD:END --> в index.html.
Все тексты лежат в HTML на листовых элементах с data-ru / data-en (их читают переключатель языка,
build_en.py и поисковые краулеры); состояние демо хранится в классах, скрипт текстов не содержит.
Запуск: py -3.12 build_demo.py && py -3.12 build_en.py
"""
import html
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
START, END = "<!-- KD:START -->", "<!-- KD:END -->"


def attr(v: str) -> str:
    return html.escape(v, quote=True)


def leaf(tag: str, t: dict, cls: str = "", extra: str = "") -> str:
    """Листовой элемент с текстом на двух языках (внутри — русский, как во всём index.html)."""
    c = f' class="{cls}"' if cls else ""
    return f'<{tag}{c}{extra} data-ru="{attr(t["ru"])}" data-en="{attr(t["en"])}">{html.escape(t["ru"], quote=False)}</{tag}>'


def fmt(t: dict, **kw) -> dict:
    return {k: v.format(**kw) for k, v in t.items()}


def panel(n: dict, ui: dict, first: bool) -> str:
    s_n, f_n, a_n = len(n["stages"]), len(n["fields"]), len(n["autos"])
    o = [0]

    def step(gap: int) -> str:
        """Порядок и пауза появления в фазе сборки (data-o — порядок, data-g — пауза до следующего, мс)."""
        o[0] += 1
        return f' data-ph="3" data-o="{o[0]}" data-g="{gap}"'

    def log(t: dict, times: int = 0) -> str:
        x = f" ×{times}" if times else ""
        both = {"ru": t["ru"] + x, "en": t["en"] + x}
        return leaf("code", both, "kd-i", "{STEP}")

    # порядок сборки: имя воронки → этапы → поля → автоматизации → пример заявки → итог
    name = leaf("span", n["pipeline"], "kd-bname kd-i", step(180))
    log1 = log(ui["log_pipeline"]).replace("{STEP}", step(260))
    cols = []
    for i, st in enumerate(n["stages"]):
        inner = f'<span class="kd-n">{i + 1}</span>' + leaf("span", st, "kd-st")
        if i == 0:
            inner += "{LEAD}"
        cols.append(f'<div class="kd-col kd-i"{step(140)}>{inner}</div>')
    log2 = log(ui["log_stage"], s_n).replace("{STEP}", step(260))
    fields = [leaf("span", f, "kd-f kd-i", step(120)) for f in n["fields"]]
    log3 = log(ui["log_field"], f_n).replace("{STEP}", step(260))
    autos = [leaf("div", a, "kd-a kd-i", step(320)) for a in n["autos"]]
    log4 = log(ui["log_auto"], a_n).replace("{STEP}", step(420))
    lead = (f'<div class="kd-lead kd-i"{step(520)}>' + leaf("span", n["lead"], "kd-lt") + "</div>"
            + leaf("span", n["task"], "kd-task kd-i", step(520)))
    cols[0] = cols[0].replace("{LEAD}", lead)
    done = leaf("span", fmt(ui["done"], s=s_n, f=f_n, a=a_n))
    done_step = step(0)

    opts = "".join(leaf("button", op, "kd-opt", ' type="button"') for op in n["opts"])
    plan = "".join(leaf("li", t) for t in (
        fmt(ui["plan_pipeline"], name=n["pipeline"]["ru"]) | {"en": ui["plan_pipeline"]["en"].format(name=n["pipeline"]["en"])},
        fmt(ui["plan_stages"], n=s_n), fmt(ui["plan_fields"], n=f_n), fmt(ui["plan_autos"], n=a_n)))
    hidden = "" if first else " hidden"
    return f"""      <div class="kd-panel" data-niche="{n['id']}"{hidden}>
        <div class="kd-chat">
          <div class="kd-msg kd-u kd-i" data-ph="1" data-g="700">{leaf("span", n["user"])}</div>
          <div class="kd-dots kd-i" data-ph="1" data-g="900" aria-hidden="true"><i></i><i></i><i></i></div>
          <div class="kd-msg kd-k kd-i" data-ph="1" data-g="0">{leaf("span", n["q"])}<div class="kd-opts">{opts}</div></div>
          <div class="kd-dots kd-i" data-ph="2" data-g="900" aria-hidden="true"><i></i><i></i><i></i></div>
          <div class="kd-msg kd-k kd-i" data-ph="2" data-g="0">{leaf("span", ui["plan"])}<ul class="kd-plan">{plan}</ul>{leaf("button", ui["go"], "kd-go", ' type="button"')}</div>
          <div class="kd-msg kd-k kd-done kd-i"{done_step}>{done}</div>
        </div>
        <div class="kd-board">
          <div class="kd-bhead"><span class="kd-win" aria-hidden="true"><i></i><i></i><i></i></span><span class="kd-crm">CRM</span>{name}</div>
          <div class="kd-cols">{"".join(cols)}</div>
          <div class="kd-sec">{leaf("span", ui["fields"], "kd-sub")}<div class="kd-fields">{"".join(fields)}</div></div>
          <div class="kd-sec">{leaf("span", ui["autos"], "kd-sub")}<div class="kd-autos">{"".join(autos)}</div></div>
          <div class="kd-log" aria-hidden="true">{log1}{log2}{log3}{log4}</div>
        </div>
      </div>"""


def main() -> None:
    data = json.load(io.open(os.path.join(HERE, "demo_data.json"), encoding="utf-8"))
    ui, niches = data["ui"], data["niches"]
    chips = "".join(
        leaf("button", n["chip"], "kd-chip", f' type="button" data-niche="{n["id"]}" aria-pressed="{"true" if i == 0 else "false"}"')
        for i, n in enumerate(niches))
    frag = f"""{START}
    <div class="kd reveal" id="kd">
      <div class="kd-top">
        {leaf("span", ui["label"], "kd-label")}
        <div class="kd-chips" role="group" aria-labelledby="kdPick">{leaf("span", ui["pick"], "kd-pick", ' id="kdPick"')}{chips}</div>
      </div>
{chr(10).join(panel(n, ui, i == 0) for i, n in enumerate(niches))}
      <div class="kd-foot">
        {leaf("span", ui["note"], "kd-note")}
        <div class="kd-btns">{leaf("button", ui["again"], "kd-again", ' type="button"')}{leaf("button", ui["cta"], "kd-cta", ' type="button"')}</div>
      </div>
    </div>
    {END}"""
    p = os.path.join(HERE, "index.html")
    s = io.open(p, encoding="utf-8").read()
    a, b = s.index(START), s.index(END) + len(END)
    s = s[:a] + frag + s[b:]
    io.open(p, "w", encoding="utf-8", newline="\n").write(s)
    print(f"demo: {len(niches)} niches, fragment {len(frag) // 1024} KB")


if __name__ == "__main__":
    main()
