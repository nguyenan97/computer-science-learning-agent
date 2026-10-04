# Bản đồ dependency của chương trình

> **File được generate — không chỉnh sửa thủ công.**  
> Canonical curriculum facts nằm trong:
> - [IUH Master of Computer Science](../../curricula/iuh/master/curriculum.md)
> - [IUH PhD in Computer Science](../../curricula/iuh/phd/curriculum.md)
>
> Generate lại bằng `python scripts/generate_curriculum_map.py`. CI dùng `--check` để phát hiện drift.

## Ownership model

File này là **derived planning view**, không phải curriculum source thứ ba.

- Hai canonical curriculum file sở hữu **course name, code, credit, objective, outcome, prerequisite, co-requisite, research component và source inconsistency**.
- Generated map chỉ sở hữu **navigation, explicit relationship extraction và learning-agent synthesis**.
- Nếu map mâu thuẫn với canonical curriculum, canonical curriculum luôn được ưu tiên.
- Các phần có nhãn **Learning-agent synthesis** là relationship phục vụ sequencing/interleaving và **không phải prerequisite chính thức của IUH**.

---

## Master track — generated course index

| Mã | Học phần |
|---|---|
| `6012401` | Philosophy — Triết học |
| `6011401` | English — Tiếng Anh |
| `6001111` | Advanced Database — Cơ sở dữ liệu nâng cao |
| `6001114` | Computational Statistics — Thống kê tính toán |
| `6001115` | Advanced Artificial Intelligence — Trí tuệ nhân tạo nâng cao |
| `6001127` | Advanced Algorithms — Thuật toán nâng cao |
| `6001130` | Advanced Data Mining — Khai phá dữ liệu nâng cao |
| `6001122` | Natural Language Processing — Xử lý ngôn ngữ tự nhiên |
| `6001121` | Information Security & Safe — An toàn và bảo mật thông tin |
| `6001124` | Parallel Computing — Tính toán song song |
| `6001129` | Text and Web Analytics — Phân tích văn bản và Web |
| `6001210` | Leadership Development — Phát triển năng lực lãnh đạo |
| `6001219` | Risk Analysis — Phân tích rủi ro |
| `6001132` | Special Topic — Chuyên đề |
| `6001131` | Digital Image Processing — Xử lý ảnh số |
| `6001223` | Deep Learning — Học sâu |
| `6001212` | Pattern Recognition and Analysis — Nhận dạng và phân tích mẫu |
| `6013400` | Scientific Research Methodology — Phương pháp nghiên cứu khoa học |
| `6001218` | Information Theory — Lý thuyết thông tin |
| `6001220` | Internet Technology of Modern Things — Công nghệ IoT hiện đại |
| `6001222` | Data Processing on Cloud Computing — Xử lý dữ liệu trên điện toán đám mây |
| `6001221` | Big Data Analytics — Phân tích dữ liệu lớn |
| `6001126` | Data Analysis Applications — Ứng dụng phân tích dữ liệu |
| `6001225` | Data Visualization — Trực quan hóa dữ liệu |
| `6001229` | Master Thesis — Luận văn Thạc sĩ |

### Relationship trích trực tiếp từ Master curriculum

| Học phần | Prerequisite/corequisite trích từ canonical source |
|---|---|
| Advanced Artificial Intelligence — Trí tuệ nhân tạo nâng cao (`6001115`) | Tiên quyết: Artificial Intelligence |
| Advanced Data Mining — Khai phá dữ liệu nâng cao (`6001130`) | Tiên quyết: Advanced Artificial Intelligence; Advanced Database |
| Natural Language Processing — Xử lý ngôn ngữ tự nhiên (`6001122`) | Tiên quyết: Artificial Intelligence, Machine Learning, Deep Learning |
| Digital Image Processing — Xử lý ảnh số (`6001131`) | Tiên quyết: Calculus 2, Programming Techniques, Data Structures and Algorithms |
| Deep Learning — Học sâu (`6001223`) | Tiên quyết: Artificial Intelligence; Học song hành: Machine Learning |
| Pattern Recognition and Analysis — Nhận dạng và phân tích mẫu (`6001212`) | Tiên quyết: Statistics Computing and Applications; Advanced Artificial Intelligence |
| Internet Technology of Modern Things — Công nghệ IoT hiện đại (`6001220`) | Tiên quyết: Artificial Intelligence; Học song hành: Deep Learning |

### Research preparation được source hỗ trợ

Canonical Master curriculum hỗ trợ preparation path sau, nhưng không định nghĩa mọi mũi tên là formal prerequisite:

`Scientific Research Methodology` → `Special Topic / focused literature work` → `Master Thesis`

---

## PhD track — generated course/research index

| Mã | Học phần |
|---|---|
| `6201100` | Deep Learning — Học sâu |
| `6201109` | Big Data Analytics — Phân tích dữ liệu lớn |
| `6201101` | Modern Networking and Communication Technologies — Công nghệ mạng và truyền thông hiện đại |
| `6201102` | Advanced Computer Vision — Thị giác máy tính nâng cao |
| `6201103` | Modern Information Systems Security — An toàn hệ thống thông tin hiện đại |
| `6201104` | High Performance Computing — Tính toán hiệu năng cao |
| `6201105` | Parallel Programming for Multicore Systems — Lập trình song song cho hệ thống đa lõi |
| `6201106` | Modeling and Simulation Techniques — Kỹ thuật mô hình hóa và mô phỏng |
| `6201301` | Literature Review — Tổng quan nghiên cứu |
| `6201200` | Research Topic 1 — Chuyên đề nghiên cứu 1 |
| `6201201` | Research Topic 2 — Chuyên đề nghiên cứu 2 |
| `6201999` | PhD Thesis — Luận án Tiến sĩ |

### Relationship trích trực tiếp từ PhD curriculum

| Học phần | Prerequisite/corequisite trích từ canonical source |
|---|---|
| Advanced Computer Vision — Thị giác máy tính nâng cao (`6201102`) | Image Processing (học trước), Computer Vision (tiên quyết), Deep Learning (học song hành) |

### Doctoral research sequence được source hỗ trợ

`Literature Review` → `Research Topic 1` → `Research Topic 2` → `PhD Thesis`

PhD curriculum cũng xác định supplementary knowledge ở mức Master's cho candidate cần bổ sung nền tảng; detailed shared foundation vẫn nằm trong canonical Master curriculum thay vì duplicate ở đây.

---

## Learning-agent synthesis

Các relationship dưới đây là instructional planning rule. Chúng kết nối official course content thành learning graph có thể sử dụng, nhưng không được trình bày như formal university prerequisite trừ khi canonical curriculum ghi rõ.

### Master knowledge dependencies

- **Computational Statistics — Thống kê tính toán** → Pattern Recognition, Data Mining evaluation, model evaluation và empirical analysis.
- **Advanced Algorithms — Thuật toán nâng cao** → AI search/optimization, graph/web analytics, scalable computation.
- **Advanced Database — Cơ sở dữ liệu nâng cao** → Data Mining, Big Data Analytics và Cloud Data Processing.
- **Advanced Artificial Intelligence — Trí tuệ nhân tạo nâng cao** → Data Mining, Pattern Recognition, Deep Learning và NLP foundation.
- **Deep Learning — Học sâu** → modern NLP, Computer Vision và AI-enabled IoT application.
- **Parallel Computing — Tính toán song song** → Big Data execution, scalable ML và distributed/high-performance processing.
- **Scientific Research Methodology — Phương pháp nghiên cứu khoa học** → research design, Special Topic và thesis preparation.

### Bridge từ Master → PhD

- **Deep Learning** → PhD Deep Learning và Advanced Computer Vision.
- **Parallel Computing** → High Performance Computing và Parallel Programming for Multicore Systems.
- **Advanced Data Mining / Big Data Analytics** → PhD Big Data Analytics.
- **Information Security & Safe** → Modern Information Systems Security.
- **Digital Image Processing / Pattern Recognition** → Advanced Computer Vision.
- **IoT / Cloud Data Processing** → Modern Networking and Communication Technologies.
- **Master Thesis / research methodology** → Literature Review, Research Topic 1/2 và doctoral thesis practice.

### High-value interleaving pairs

- database indexing ↔ algorithm complexity
- hypothesis testing ↔ experiment / A-B-test reasoning
- entropy ↔ decision tree / cross-entropy reasoning
- graph algorithm ↔ web analytics
- concurrency control ↔ distributed-system consistency
- parallelism ↔ Big Data execution plan
- security ↔ cloud / IoT architecture
- model evaluation ↔ statistical inference
- visualization ↔ decision quality
- research methodology ↔ mọi empirical mini-project

---

## Maintenance contract

Khi canonical curriculum thay đổi:

1. Chỉ sửa source `curricula/iuh/.../curriculum.md` tương ứng.
2. Cập nhật bản dịch curriculum trong `vi/curricula/iuh/.../curriculum.md`.
3. Chạy `python scripts/generate_curriculum_map.py`.
4. Review diff của cả hai curriculum map.
5. Nếu conceptual sequencing thay đổi, cập nhật phần **Learning-agent synthesis** trong generator rồi generate lại.
6. Chạy `python scripts/generate_curriculum_map.py --check` trước khi commit.

Cách này giữ official curriculum fact ở một nơi nhưng vẫn cung cấp dependency graph song ngữ cho topic selection của learning agent.
