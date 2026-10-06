# Vietnamese style and glossary for lessons

Lessons are for working developers (.NET, Angular, SQL Server, Azure). Write Vietnamese
the way a team talks in standup: Vietnamese sentences, English technical vocabulary.
Rule of thumb: if engineers say the English word at work, keep it. If you must pick a
Vietnamese word, it must be one people actually say; otherwise keep English and gloss it once.

## Keep in English (gloss once on first use)

| Keep | First-use gloss (Vietnamese) | Do not write |
|---|---|---|
| duplicate, dedupe / deduplicate | trùng lặp / loại bỏ trùng lặp | khử trùng |
| hash, hash table, bucket, collision | - | băm, bảng băm, xô, va chạm (dùng lẫn lộn) |
| Big-O, cost model | thang đo độ tăng chi phí; mô hình chi phí | chặn trên của tốc độ tăng |
| worst case, average case, expected case | trường hợp tệ nhất / trung bình / kỳ vọng | trường hợp xấu |
| amortized | chi phí trung bình khi gộp nhiều thao tác | khấu hao |
| trace, invariant, edge case | lần lượt chạy tay; điều luôn đúng; trường hợp biên | vết, bất biến (một mình) |
| benchmark, allocation, GC, peak memory | - | điểm chuẩn, cấp phát (một mình) |
| scan, lookup, resize, batch, prefix | - | quét tuần tự, tra cứu (khi đã quen dùng lookup) |
| idempotency, unique constraint/index, race condition | - | - |
| contract, requirement | hợp đồng hành vi: input/output/lỗi được cam kết | hợp đồng |

Use Vietnamese for ordinary words: chạy, kiểm tra, so sánh, bước, kết quả, giả định, ví dụ.
Technical terms outside this table follow the same rule; add them here when introduced.

## Typography

Plain hyphen `-` only. No em dash `—` or en dash `–`. Ranges: `0-20`. Titles: `Bài 01 - ...`.

## Check before publishing

1. Read each Vietnamese paragraph aloud: would a colleague say this? If not, rewrite it.
2. Any invented or literal-translated term? Replace it with the kept English term.
3. Each kept term glossed once, near its first use, in the concept primer.
4. No `—` or `–` anywhere in `lesson.md`, catalog titles, recall entries or lab README.
