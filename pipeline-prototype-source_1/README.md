# 24.online — Enhance Listing prototype · сборка

Итоговый файл: `pipeline-prototype-as-is.html` (собирается из этих исходников).

## Как собрать
```
python3 build4.py        # → pipeline-prototype.html
```
Нужны: Python 3, Pillow. build4.py импортирует куски из build2.py и gpatch.py.

## Что где
- `template4.html` — весь мой каркас: шаги 1–4 и 7, CSS, JS-склейка (PX.*), редактор-модал, апселл, ZIP-скачивание, нарратор, мобильные стили. Плейсхолдеры `/*GCSS*/ /*ACSS*/ <!--GBODY--> <!--ABODY--> /*GJS*/ /*AJS*/` заполняет сборка.
- `gallery-slides-variations_19.html` — блок галереи Данияра (шаг 5). В сборке изолируется в `.sc-g`, id получают префикс `g_`.
- `aplus-briefing_39.html` — блок A+ брифа (шаг 6). Изолируется в `.sc-a`, префикс `a_`.
- `build2.py` — функции изоляции (scope_css, rename_ids), первичные патчи галереи (handoff-панель, хуки `window.startGallery`, `__galleryDone`).
- `gpatch.py` — патчи галереи для режима брифа (compact-плейсхолдеры, Edit/Comment/×, paste-list, undo, 9 слайдов, ≤60-символьные подписи, API `window.GAL`).
- `build4.py` — главная сборка: подключает всё выше, добавляет CSS-оверрайды его блоков, вшивает картинки base64.
- Картинки: `img0..5.jpg` — 6 слайдов из галереи; `a_lst*.png`, `a_main.png`, `a_apd.png`, `a_apm.png` — вырезки из макета; `Group_86.jpg` + два png — вариации главного изображения.

## Ключевые хуки между блоками
- `window.startGallery()` / `window.GAL.prepare()` — старт рендера / режим брифа.
- `window.__galleryDone`, `window.__aplusDone`, `window.__galEdit`, `window.__galBefore` — сигналы из его блоков в склейку.
- `window.APL` — API A+ брифа (get/set/count) для модального редактора.
- `PX.*` — все публичные функции склейки (run5, useVar, galApprove, download, openEditor…).
