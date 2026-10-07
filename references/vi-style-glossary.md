# Vietnamese style and terminology for lessons

Write clear Vietnamese for developers who work with .NET, Angular, SQL Server and
Azure. Use complete Vietnamese sentences, established technical terms and concrete
examples. Familiar English vocabulary can stay when it is the clearest choice, but
English nouns and verbs should not replace ordinary Vietnamese throughout a sentence.

## Explain ideas, not every English word

The opening primer teaches the few concepts needed to follow the lesson. Give each
central idea a short explanation, the question it answers and a small example. It is
not a dictionary: API, input, output, query, test, debug, duplicate and other familiar
developer words do not need entries or compulsory first-use glosses.

Introduce a less familiar idea where it becomes useful. Explain what it means in
that context rather than attach a parenthetical translation to every occurrence.
For example, explain a hash collision while showing how a hash table finds an entry,
and explain p99 when distinguishing a benchmark from service latency.

## Choose terms by meaning and context

These are examples, not a required vocabulary list. Either an established Vietnamese
term or a familiar English term can work. Be consistent within an explanation.

| Idea | Natural wording | Precision to preserve |
|---|---|---|
| duplicate / dedupe | duplicate; dedupe; loại bỏ phần tử trùng | Never use “khử trùng”: that means disinfection. State which occurrence is retained. |
| cost model | mô hình chi phí | Say what is counted: comparisons, reads, allocations or another operation. |
| Big-O | Big-O; cận trên của mức tăng chi phí | An asymptotic upper bound is not an exact time or a doubling prediction. |
| worst case / expected cost | trường hợp xấu nhất; chi phí kỳ vọng | State the input or probability assumptions. Expected cost is not simply an average over measured runs. |
| amortized analysis | phân tích amortized; xét tổng chi phí của một chuỗi thao tác | Occasional expensive operations are spread across the sequence; this does not require a probability model. |
| invariant | bất biến; điều kiện được duy trì sau mỗi bước | State the actual condition, then show why both branches preserve it. |
| hash / collision | hash; hai giá trị có cùng hash | Distinct keys can share a hash. Equality checks still decide whether the keys match. |
| lower bound | lower bound; vị trí đầu tiên có giá trị lớn hơn hoặc bằng giá trị cần tìm | Distinguish this search boundary from a lower bound on computational cost. |
| half-open interval | khoảng nửa mở `[start,end)` | Includes `start`, excludes `end`; show what happens at duplicate endpoints. |
| benchmark / allocation | benchmark; đo hiệu năng; cấp phát bộ nhớ | Say which workload is measured. Allocated bytes are not peak memory or service p99. |
| idempotency | idempotency; xử lý lặp lại không tạo thêm tác động nghiệp vụ | Define the event identity and transaction boundary before claiming duplicate delivery is safe. |
| contract | yêu cầu; quy tắc xử lý; điều kiện của hàm | Prefer a concrete statement about inputs, results and errors over “hợp đồng” without context. |

Use ordinary Vietnamese where it reads naturally: “hành vi”, “lập luận”, “đọc mã nguồn”,
“chạy từng bước”, “tra cứu”, “quét”, “tăng dung lượng”, “cấp phát”, “mục tiêu”, “điều kiện
dừng”. Do not replace these automatically with behavior, reasoning, source reading,
trace, lookup, scan, resize, allocation, objective or stop condition.

## Technical and research prose

Connect a question to the method used to answer it. Distinguish a **giả định** of the
model, a **giả thuyết** to test, a **quan sát** from an execution, and a **suy luận**
from the evidence. State the **giới hạn** when it affects the conclusion. “Nghiên cứu”
means examining a question and evidence; do not use “research” merely to make ordinary
reading sound more formal.

Keep necessary qualifications. “Kỳ vọng O(n), với chi phí xử lý khóa bị chặn và phân
bố hash phù hợp” carries meaning that “O(n)” alone loses. Remove filler, repeated
definitions, self-praise and internal verification reports, not the assumptions that
make a claim correct. Prefer an example before a formula, then explain the formula.

Section task lines say what the reader should do, for how long and when to stop.
Use labels such as “Đọc mã nguồn · 45 phút”, not internal IDs such as
“Block implementation-reading”.

## Typography and review

Use a plain hyphen `-`, never an em dash or en dash. Ranges use `0-20`; titles use
`Bài 01 - ...`.

Before publishing, read paragraphs aloud, check terminology against the actual
mechanism and source, and remove redundant words. Check that code, examples,
assumptions and conclusions agree with the English page. Common English words do
not require a glossary entry. Search lesson prose, catalog text and lab guides for
typographic dashes and awkward mixtures of English fragments and Vietnamese syntax.
