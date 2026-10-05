<!-- contract-version: 1 -->
# Tìm biên: từ mảng có thứ tự đến truy vấn khoảng thời gian

**Session:** sample-boundary-search · **Topic:** `advanced-algorithms.boundary-search.l1` · **Môn:** Advanced Algorithms `6001127` · **Loại/status:** core/generated · **Kiểm tra:** 2026-10-05. Đây là bài mẫu để review, chưa giao/hoàn thành. [Record chung](../../../lessons/boundary-search/record.json) nằm ngoài tiến độ thật; [bản Anh đầy đủ](../../../lessons/boundary-search/lesson.md).

## Lý do chọn và outcome

[Curriculum](../../curricula/iuh/master/curriculum.md) yêu cầu phân tích độ phức tạp, đánh giá performance và chọn thuật toán. Boundary search là nền do người hướng dẫn chọn, không phải bài/prerequisite được IUH quy định rõ. Chuẩn bị cho ordered indexing nhưng không đánh đồng mảng với B-tree database.

State thật trống: chưa có bài ôn/prior knowledge/core trùng. Trong phiên thật, chạy planner, hỏi goal/time/tools và thu diagnostic trước; mẫu này chỉ phù hợp khi đáp ứng prerequisite.

Người học cần tự: (1) nêu/giữ partition invariant cả duplicates/empty/missing; (2) implement không slice/mutate và chứng minh access logarithmic; (3) transfer sang count event trong `[start,end)`, giải thích endpoints/update cost.

Mode heuristic: ngắn 25 phút = 3 diagnostic + 6 model/example + 10 lab + 4 independent + 2 exit, dời đọc repo sâu; chuẩn 55 = 5 + 10 + 20 lab + 10 challenge + 5 repo + 5 feedback/exit; mở rộng 85 thêm 15 record/key và 15 research/experiment. Hết thời gian giữ in_progress.

## Retrieval và prerequisite

Không ghi chú: `[lo,hi)` chứa vị trí nào? Insert đầu mảng đổi index ra sao? Trace loop chia đôi số nguyên dương. Có history thì thay một câu bằng prompt ôn đến hạn và lưu response thật.

Diagnostic `[2,4,4,9]`: index nào có value < 4; biên trước số 4 đầu tiên? Trace lo=0,hi=4,mid=2; hi=mid có giữ answer hợp lệ không? Vì sao phải sorted?

Yếu → vẽ index, partition mảng ba phần tử, thêm duplicate và retrace. Recheck `[1,1,3]` trước code; vẫn yếu thì chỉ prerequisite hôm nay. Không tự chấm điểm/đoán mastery, ghi câu trả lời và hint.

## Vấn đề và dự đoán

Service lưu timestamps sorted, integer có duplicates; hỏi nhiều lần số event từ start inclusive đến end exclusive. Scan chạm mọi event. Binary search tìm “một giá trị bằng” có đủ khi endpoint lặp không? Thử rule vài phút rồi debrief với ví dụ; novice có thể xem ví dụ ngay.

## Nền tảng và cập nhật liên quan

**Theory:** `0<=lo<=hi<=n`; trước lo đều < x, từ hi trở đi đều >= x; đoạn chưa biết `[lo,hi)`. lo==hi xác định biên, kể cả n. Ở mid: value < x thì bỏ đến mid; ngược lại giữ mid là biên tiềm năng. Mỗi bước giảm xấp xỉ nửa; random-access array cần O(log n) comparisons/access, O(1) space. Insert list vẫn O(n) do dịch phần tử. Sorted/order consistent là assumption; key/access đắt hay input unsorted làm đổi cost/semantics.

**Official implementation, baseline đã ghim:** `bisect_left` tìm partition, không tìm equality; key áp vào record trong mảng nhưng không áp vào x tìm kiếm. `insort` có search logarithmic nhưng insert linear. Đã đọc source/doc theo SHA; release lịch sử không phải khuyến nghị support/security mới nhất, cần check lúc học thật.

**Instructor synthesis:** reasoning biên sang range query được; array complexity không dự đoán disk I/O, plan, collation hay write amplification database.

## Worked example nêu quyết định

`[1,3,3,8]`, x=3: (lo,hi,mid)=(0,4,2), value 3 → hi=2 vì equality thuộc partition phải và có thể có 3 trước; (0,2,1), value 3 → hi=1; (0,1,0), value 1 → lo=1 vì index 0 nhỏ hơn; (1,1) → return 1. Vì sao return ngay mid khi equality chỉ cho một matching index mà không phải boundary? Giải thích trước code; solution window vẫn được giữ riêng.

## Lab hướng dẫn từng bước

Goal: implement và giải thích invariant. Python 3.12.x, standard library, không network/package/data ngoài; Linux/macOS/Windows với shell tương đương. Đã chạy Python 3.12.14. Test sinh integer deterministic. Python giảm setup cho mục tiêu partition; .NET/SQL dùng khi hợp bài sau.

Từ repo root:

```bash
cd labs/boundary-search
python --version
python observe.py
```

Không có Python phù hợp → runtime compatible ghi version hoặc trace giấy, không coi chưa chạy/trace giấy là code execution. Không cần build CPython.

1. **Specification:** predict `bisect_left([2,4,4,9],4)` và x=5 trước observer; kiểm tra inequalities. Checkpoint: 1 và 3. Giải thích missing value vẫn có insertion boundary.
2. **Cost:** predict access khi n=8/1024/65536. Chạy observer; checkpoint index=4/512/32768, reads=3/10/16 trong runtime đã verify. Đây không là wall-clock benchmark; giải thích key/insert cost khác.
3. **Trace trước code:** x=0/x=10 và empty; mỗi iteration giảm hi-lo, biên 0/4. Vì sao hi=mid-1 có thể phá half-open invariant?
4. **Faded example:** chỉ điền `lower_bound` trong starter.py: init unknown interval, loop nonempty, midpoint, chọn update từ partition, return boundary. Không mutate/slice/built-in search. Predict duplicate/all-smaller trước check.
5. **Checkpoint/debug:** chạy guided check, oracle standard library cho sorted multisets dài 0–6, partition/input preservation và access budget dữ liệu lớn. Đúng → 2 tests pass; starter chưa điền cố ý NotImplementedError. Trace case nhỏ nhất in ra, không paste oracle.

```bash
python check.py --stage guided
```

Explain-after: nhánh nào giữ từng phần invariant, test access đo gì/không đo gì? Lưu revision, trace và output thật. Infinite loop → interval shrink; duplicate sai → equality; empty IndexError → condition; x>max → cho return n; import/path → dùng lab directory; tool fail → lưu version/error và trace offline trong khi sửa setup.

## Research GitHub và hoạt động đọc

Chọn official [python/cpython](https://github.com/python/cpython): **77.489 stars**, archived=false, check 2026-10-05 từ embedded HTML. Commit branch mới quan sát `5fecd448bb120378978a37dde65dfce233d88c0d` lúc 2026-10-05 01:49:56 UTC. API không truy cập; [metadata/hashes](../../../lessons/boundary-search/repository-evidence.json). Pin v3.12.7 → **0b05ead877f909b7efe712db758012d9dbece7ce**, baseline tái lập, không claim latest.

Authority chính thức Python, practical relevance trực tiếp; chưa khảo sát định lượng downstream adoption. Code nhỏ, docs nêu assumption/performance; tests có duplicate/random/bounds/key. Đã đọc PSF license, không vendor upstream code, không chạy full build/benchmark. CPython toàn repo phức tạp nên chỉ đọc slice. Alternative official dotnet/runtime có **18.311 stars**, không archived, metadata check cùng ngày; không chọn vì setup/build vượt nhu cầu partition và local Python chạy được, không kết luận chất lượng kém hơn.

Ở pin trên, đọc các target cụ thể:

- [Lib/test/test_bisect.py](https://github.com/python/cpython/blob/0b05ead877f909b7efe712db758012d9dbece7ce/Lib/test/test_bisect.py): `TestBisect.precomputed`, `test_precomputed`, `test_random`, `test_lookups_with_key_function`; suy left/right và giải thích một case duplicate trước đọc implementation.
- [Lib/bisect.py](https://github.com/python/cpython/blob/0b05ead877f909b7efe712db758012d9dbece7ce/Lib/bisect.py): trace `bisect_left`, so `bisect_right`; giải thích `_bisect` có thể thay function lúc import. Observer dùng interpreter đã cài, không chạy historical Python source này.
- [Doc/library/bisect.rst](https://github.com/python/cpython/blob/0b05ead877f909b7efe712db758012d9dbece7ce/Doc/library/bisect.rst): partition/key/performance notes; predict search record khi x là key và nối cost.
- [LICENSE](https://github.com/python/cpython/blob/0b05ead877f909b7efe712db758012d9dbece7ce/LICENSE): xem quyền trước reuse.

Network lỗi → local lab, ghi không đọc được upstream, không bịa. Mode ngắn dời đọc sâu, không biến bài thành danh sách link.

## Challenge độc lập và biến thể transfer

Không mở mentor, implement `count_window` trong starter.py: sorted integer timestamps, đếm start<=t<end; input không đổi; endpoints bằng nhau/empty hợp lệ; end<start raise ValueError. Không scan/slice/sort mỗi query. Tự thiết kế ít nhất ba test duplicate endpoint/empty window/missing endpoint và predict trước chạy.

```bash
python check.py --stage all
```

Đúng → 4 tests pass. Đây là transfer sang context mới gần, không chứng minh mọi database. Mở rộng: event record dùng timestamp key, phân biệt x key với full record; assumption sorted/timezone; workload nhiều insert khiến flat list kém phù hợp, so ordered index với cost model riêng.

Hint/solution trong mentor riêng; chỉ mở theo attempt/request/worked review. Hint conceptual → structural → implementation. Ghi hint thật, assisted không independent.

## Rubric, feedback và exit

| Outcome | Bằng chứng đạt | Feedback / recheck |
|---|---|---|
| Partition | edge cases/inequalities/input nguyên | Counterexample nhỏ, sửa nhánh và trace mới |
| Reasoning/cost | invariant/termination/access bound; insert cost riêng | Nếu nghĩ insert log n, dự đoán số phần tử dịch |
| Independence/transfer | window/tests mới không hint, endpoint/validation | Lưu hint/error, đổi data/context trước chấm lại |
| Explain | mechanism/assumption/counterexample/trade-off | Vì sao equality match chưa đủ; so record/scalar |

Outcome qualitative needs_support/developing/independent/unassessed, không gate điểm cố định. Suite pass là artifact, không mastery. Lưu lỗi gốc, feedback/hint, giải thích sửa và lần thử mới.

Explain-back: invariant bằng lời mình; equality branch; data structure cho nhiều đọc/nhiều insert. Exit không ghi chú: tái dựng partition x absent; predict window endpoint lặp; vì sao database index không phải Python list và cần cost model gì?

## Nguồn nghiên cứu và review hooks

Curriculum outcome `6001127` đã đọc 2026-10-05, không quy định sequence cụ thể. CPython source/test/docs chính thức ở pin đã đọc cùng ngày cho contract/key/insert cost, không claim support latest. [Deans for Impact 2015](https://github.com/carpentries/instructor-training/blob/50745001271700a108de0622d80341965e249e5b/episodes/files/papers/science-of-learning-2015.pdf), câu 1–4 đã đọc cùng ngày, hỗ trợ scaffolding/retrieval/spacing/transfer cấu trúc; giới hạn primary access trong [report](../../research/learning-science-review.md). Diagnostic, trace, time và rubric là instructor design cần đo, không tối ưu đã chứng minh.

Sau completion thật, chọn due với người học theo performance/retention goal. Prompt A tái dựng invariant và duplicate boundary mới không hint; prompt B sau đó window đổi context và update-heavy trade-off. Sai/hint → correction và retry sớm hơn; independent giải thích tốt → cân nhắc gap dài hơn. Giữ ngày hẹn/ngày quan sát/reason đổi. Chưa ghi review hay mastery cho bài mẫu chưa giao.

Khi giao thật, tạo session riêng và copy starter vào workspace đó. Record mẫu công khai không vào progress thật; không import sample ID.
