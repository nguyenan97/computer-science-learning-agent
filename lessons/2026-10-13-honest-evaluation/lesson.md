# Lesson 09 - Honest evaluation: learn a rule without learning the test

[Tiếng Việt](../../vi/lessons/2026-10-13-honest-evaluation/lesson.md) · [Download the C# lab](https://nguyenan97.github.io/computer-science-learning-agent/labs/honest-evaluation/dotnet-lab.zip)

An ASP.NET support service wants to flag tickets likely to miss a 24-hour deadline. A rule that never flags anything can look accurate while missing every late ticket. A more elaborate rule can look perfect if its input already reveals the eventual outcome. Neither score answers whether the rule can help at ticket arrival.

**Goal:** fit a small threshold model, compare it with two baselines, justify a train/validation/test boundary and explain errors under a declared cost. The planner selects learning-system evaluation after experimental design. We reuse observation units, model assumptions, invariants and independent checks. Features, labels, fitting, held-out evaluation and classification metrics are introduced here; no previous machine-learning course is assumed.

## Main ideas

- **Learning chooses a rule from examples.** Historical tickets with intake scores and eventual outcomes help choose a cutoff. The cutoff is fitted; the outcome of a new ticket is still unknown when the rule acts.
- **Evaluation needs an information boundary.** Learn from train, choose among candidates with validation, then audit a frozen choice on test. A deadline outcome copied into an intake feature crosses that boundary even if row IDs differ.
- **Different errors have different consequences.** Missing a late ticket and unnecessarily escalating an on-time ticket are different mistakes. A count of correct predictions alone hides that difference.
- **The unit defines the claim.** New tickets from known customers and tickets from entirely new customers are different targets. Holding out rows can still expose the same customer's history.

Use worked traces and closed answers as a reading-only route. Limit lab setup to 15 minutes of its block. All ticket data and cost units are synthetic; this lesson measures no production latency or business savings.

## 1. Recall the boundary before adding a model

**Recall · 20 minutes.** Reconstruct the three planner-selected answers and connect them to information available when a decision is made. **Done when:** each answer includes its assumption and a boundary case.

1. Why does a randomized pair contrast target the fixed-cohort average effect but not recover every individual effect?

<details>
<summary>Answer</summary>

The two equally likely orientations average half the sum of the pair effects; averaging pairs gives tau in assignment expectation. Each real unit exposes only its received outcome. This needs the stated allocation, consistency/no interference and complete outcomes; random assignment does not make the cohort representative.

</details>

2. Why must a stale WAL read transaction end before reconsidering a write?

<details>
<summary>Answer</summary>

Its end mark stays fixed; after another commit, promotion can return BUSY_SNAPSHOT. End/roll back that transaction, read fresh state and redo the bounded decision. Waiting or repeating the old snapshot does not refresh it.

</details>

3. How do you decode a negative .NET BinarySearch result, and can a successful result replace lower_bound when duplicates exist?

<details>
<summary>Answer</summary>

If r<0, the insertion index is ~r, not -r. On a hit, Array.BinarySearch/List<T>.BinarySearch may return any matching index, so use an explicit lower_bound for the first duplicate or for exact [start,end) counting. The input must be sorted by the same comparer.

</details>

The connection is an information contract, not equivalence between these mechanisms. A transaction snapshot governs database visibility. A test boundary governs which observations may influence model choice. Binary search needs a particular ordering contract. Random assignment concerns causal effects, whereas predicting a late ticket concerns unseen outcomes. A predictive score does not establish the effect of actually escalating a ticket.

## 2. From a ticket example to a learning argument

**Foundation · 50 minutes.** Complete the prediction trace, reconstruct the cutoff search and state both invariants. **Done when:** you can distinguish optimal training loss from an honest assessment on new observations.

### Define what is known and what is learned

At intake, ticket `te7` has a synthetic workload score 7. Its label is 1 because it eventually misses the deadline. The rule `score >= 5` predicts 1 immediately; the label is collected only after the outcome window. The score here is an integer feature 0-9, not a probability or a calibrated risk estimate. Think of it as a fixed transformation of intake backlog; the lab directly supplies it rather than validating a production feature pipeline.

A **feature** is information used to predict, such as backlog known at intake. A **label** is the outcome to be predicted, here late=1/on-time=0. **Binary classification** chooses one of those two labels. A **model** is the prediction rule plus any learned state; ours stores a threshold. **Fitting** chooses that state from labelled training examples. This is supervised learning because outcomes accompany the examples. It needs neither a neural network nor gradient descent.

We allow thresholds 0 through 10. Threshold 0 flags every valid score; threshold 10 flags none. A training-majority baseline picks whichever constant label is more frequent, with label 0 on a tie. A fixed-rule baseline uses cutoff 7 without fitting. Neither baseline is automatically useless: they make the claim of improvement concrete.

Before examining validation/test results, declare a false-positive cost of 1 and a false-negative cost of 4. These are invented decision units, not dollars. Correct decisions cost 0 in this simplified model. Real escalation costs can also arise for true positives, consume shared capacity and change outcomes; those effects are outside this additive loss.

### Trace predictions before writing ratios

The synthetic test fixture has scores 0-9 once each; labels are 1 only at 4,7,9. Complete the running confusion counts for threshold 5. Identify an unnecessarily flagged ticket and a missed late ticket.

<details>
<summary>Answer</summary>

| Score | Actual label | Predicted label | Cell added | Running TP/FP/FN/TN |
|---|---|---|---|---|
| 0 | 0 | 0 | TN | 0/0/0/1 |
| 1 | 0 | 0 | TN | 0/0/0/2 |
| 2 | 0 | 0 | TN | 0/0/0/3 |
| 3 | 0 | 0 | TN | 0/0/0/4 |
| 4 | 1 | 0 | FN | 0/0/1/4 |
| 5 | 0 | 1 | FP | 0/1/1/4 |
| 6 | 0 | 1 | FP | 0/2/1/4 |
| 7 | 1 | 1 | TP | 1/2/1/4 |
| 8 | 0 | 1 | FP | 1/3/1/4 |
| 9 | 1 | 1 | TP | 2/3/1/4 |

Scores 5,6,8 are unnecessary flags; score 4 is a miss. Six of ten predictions are correct, two of five flags are correct, and two of three late tickets are found. Cost is three unnecessary flags plus four units for the missed ticket, or 7. This is a public teaching fixture; a real final test would not be revealed during development.

</details>


TP means predicted 1/actual 1; FP means predicted 1/actual 0; FN means predicted 0/actual 1; TN means predicted 0/actual 0. The confusion matrix separates those four counts. With N nonempty observations, write:

```text
accuracy  = (TP + TN) / N
precision = TP / (TP + FP), when TP + FP > 0
recall    = TP / (TP + FN), when TP + FN > 0
loss      = FP + c * FN, where c is the declared missed-ticket cost
mean loss = loss / N
```

Precision answers how many flags were correct; recall answers how many late tickets were found. Undefined denominators are not evidence of perfect performance. The lab returns null and prints `undefined`, rather than silently inventing a value. A never-flag baseline here has 70% accuracy, recall 0 and cost 12. Threshold 5 has 60% accuracy but cost 7. A separate 100-ticket cohort with 99 on-time tickets gives that same baseline 99% accuracy while missing its only late ticket. Class frequency and error cost must be stated.

The count-loop invariant is that after processing a prefix, the four cells count exactly the corresponding outcomes in that prefix and sum to its length. Initially all are zero. Exactly one mutually exclusive cell increases for every row; termination therefore gives the complete table. This proves the counting mechanism under valid binary inputs, not label quality or future performance.

### Fit by an explicit finite search

Train has twenty tickets: two at each score 0-9. Scores 0-4 have no late tickets; scores 5,6,7 each have one late and one on-time ticket; scores 8,9 each have two late tickets. For each cutoff, count mistakes on **train only**. We fit one candidate with c=1 and another with c=4. Compute the selected thresholds with a largest-threshold tie rule.

<details>
<summary>Answer</summary>

| Cutoff | Train FP | Train FN | Loss c=1 | Loss c=4 |
|---|---|---|---|---|
| 0 | 13 | 0 | 13 | 13 |
| 1 | 11 | 0 | 11 | 11 |
| 2 | 9 | 0 | 9 | 9 |
| 3 | 7 | 0 | 7 | 7 |
| 4 | 5 | 0 | 5 | 5 |
| 5 | 3 | 0 | 3 | 3 |
| 6 | 2 | 1 | 3 | 6 |
| 7 | 1 | 2 | 3 | 9 |
| 8 | 0 | 3 | 3 | 12 |
| 9 | 0 | 5 | 5 | 20 |
| 10 | 0 | 7 | 7 | 28 |

With c=1, cutoffs 5-8 tie at loss 3; choose 8. With c=4, cutoff 5 uniquely minimizes loss. The fit is choosing a parameter from data, not manually assigning a cutoff after inspecting test. A smaller training loss need not survive validation or test.

</details>


Formally, let `h_t(x)=1` if `x>=t`, otherwise 0. The empirical training objective is `L_train(t)=sum_i loss(h_t(x_i),y_i)`. Empirical means computed on the observed sample. `Fit` returns the largest t among minimizers over `{0,...,10}`. Every real-valued threshold on integer scores 0-9 has the same predictions as one of these eleven candidates, including constant extremes. This completeness is specific to the input domain and the `>=` direction; it does not cover arbitrary multi-feature rules.

The search invariant: after cutoff t, `bestCost` is the minimum over cutoffs 0 through t, and `best` is the largest minimizer there. The first candidate initializes it. A strictly smaller cost replaces the minimum; an equal cost replaces the earlier cutoff because enumeration increases. A larger cost preserves both properties. Termination yields an empirical optimum in the declared family. The independent checker enumerates in reverse and uses strict `<`, checking the same tie rule without copying the search update.

For n rows and T candidates, rescanning costs O(T*n) plus validation; our T=11 is fixed, so row work is linear. Hash-based ID validation uses O(n) memory and expected linear work with bounded key costs and suitable hash distribution. Arbitrarily long/adversarial IDs add cost, as in Lesson 01. This teaching search is deliberately simple, not a high-throughput trainer.

### Separate selection from the final audit

Here train contains 20 rows from 10 customers, validation 10 rows from 10 other customers, and test 10 rows from 10 more customers. No customer appears in two partitions. The target is tickets from **unseen customers**, with features available at intake and outcomes collected after 24 hours. Partitions are deterministic fixtures, not random samples or evidence of customer independence.

Train produces two fitted candidates and the majority baseline. Compare those and the prespecified cutoff-7 baseline on validation using the same declared c=4. Validation labels may choose a candidate; they are therefore not untouched final evidence. Candidate order resolves validation-loss ties. Complete the selection ledger.

<details>
<summary>Answer</summary>

| Candidate | Cutoff learned/fixed | Validation FP/FN | Validation cost c=4 |
|---|---|---|---|
| Majority | 10 from train | 0/4 | 16 |
| Fixed rule | 7 before fitting | 0/1 | 4 |
| Fit with c=1 | 8 from train | 0/2 | 8 |
| Fit with c=4 | 5 from train | 1/0 | 1 |

Freeze cutoff 5. In this protocol there is no refit on train+validation, so the audited rule is exactly that selected candidate. A refit policy could be valid if declared in advance and audited afterward; it creates a new fitted object and must not use test labels.

</details>


A frozen predictor h and a new observation independent of its train/selection data allow the expectation argument from Lesson 07: if test observations share the target distribution, each expected loss equals target risk `R(h)`, so the expected mean test loss equals `R(h)` by linearity. Independence between test observations is needed for the usual simple variance/interval calculations; expectation itself needs the appropriate common marginals. Our fixed synthetic table does not establish those assumptions.

Selecting the smallest test loss instead makes h depend on those test outcomes. Its reported minimum is optimistically selected evidence, not an untouched audit. A perfectly counted test can therefore assess the wrong procedure. Validation is also reusable only with care: many adaptive searches can overfit it. Here overfitting means tailoring choices to peculiarities of the observed validation set instead of patterns that persist in new data. A large future project may need nested evaluation or a fresh audit; neither is implemented today.

Pause - 10 minutes away from the screen.

## 3. Read what an evaluation score can claim

**Source reading · 45 minutes.** Read the bounded documentation and write a claim/evidence/limit ledger. **Done when:** you can defend one evaluation protocol and identify a score that does not support its deployment claim.

Read scikit-learn's [common pitfalls, lines 15-224](https://github.com/scikit-learn/scikit-learn/blob/102e5daf66759cf896beeee229d1bf7c80ab2ba4/doc/common_pitfalls.rst#L15-L224), focusing on inconsistent preprocessing, data leakage and fitting feature selection only on train. Its random-label/high-dimensional example shows how supervised feature selection before splitting can manufacture apparent predictability. The documentation's numeric examples are source examples, not measurements reproduced by our C# lab.

Read only [accuracy, lines 575-599](https://github.com/scikit-learn/scikit-learn/blob/102e5daf66759cf896beeee229d1bf7c80ab2ba4/doc/modules/model_evaluation.rst#L575-L599), [confusion-matrix convention, lines 769-800](https://github.com/scikit-learn/scikit-learn/blob/102e5daf66759cf896beeee229d1bf7c80ab2ba4/doc/modules/model_evaluation.rst#L769-L800) and [precision/recall formulas, lines 1030-1064](https://github.com/scikit-learn/scikit-learn/blob/102e5daf66759cf896beeee229d1bf7c80ab2ba4/doc/modules/model_evaluation.rst#L1030-L1064). The library has many other metrics; we implement only binary counts, these ratios and a declared cost. Our nullable zero-denominator policy is explicit; no compatibility claim with every scikit-learn metric option is made.

Make one three-row ledger for these claims: preprocessing learned from all rows is harmless because it ignores test labels; a 99% accuracy model necessarily catches rare late tickets; and predictive accuracy proves escalating tickets reduces lateness.

<details>
<summary>Answer</summary>

| Claim | Evidence | Boundary/correction |
|---|---|---|
| All-row preprocessing is harmless | Common pitfalls says even learned scaling can use held-out distribution information | Learn preprocessing inside the training boundary; label-free does not mean evaluation-free |
| 99% accuracy catches rare positives | The 99-on-time/one-late counterexample | Report class counts, confusion cells, recall and declared cost; a constant negative rule can miss everything |
| Prediction proves an intervention works | Lesson 08 separates observed associations from potential-outcome effects | Labels may reflect existing workflow; a frozen predictive audit is not randomized escalation evidence |

The source supports boundary discipline, not the claim that every leaked transformation strictly improves every score. Leakage invalidates the intended information protocol even when its measured effect is small or negative.

</details>


If a learned transformation divides by the training mean, its mean must be frozen for validation/test. The same fitted transformation acts on all partitions; fitting it again on each partition creates inconsistent prediction rules. A fixed unit conversion that learns nothing from data is different, but availability, units and version still need checking. The threshold lab has no learned scaling; this is a source-backed extension, not a separately executed scaler experiment.

## 4. A developer tool makes the boundary executable

**Source analysis · 45 minutes.** Follow clone, split, fit and predict in one implementation path. **Done when:** your trace identifies which rows can influence fitted state and what the tool cannot detect.

scikit-learn is a widely used learning/evaluation developer tool. Its search API solves the product problem of comparing candidate parameter settings across repeated data splits without reusing one fitted estimator's state across tasks. With C candidates and K splits, the inspected code creates C*K fits and permits parallel scheduling; this costs repeated training and resources instead of simply fitting once and scoring that same fit everywhere. No runtime/memory benchmark of that trade-off was run here.

Read commit **102e5daf66759cf896beeee229d1bf7c80ab2ba4**, with these bounded slices:

- [`_search.py`, candidate dispatch, lines 1014-1103](https://github.com/scikit-learn/scikit-learn/blob/102e5daf66759cf896beeee229d1bf7c80ab2ba4/sklearn/model_selection/_search.py#L1014-L1103): clone the base estimator, enumerate candidate/split pairs, call `_fit_and_score` with a clone and the train/test indices.
- [`_validation.py`, `_fit_and_score`, lines 792-872](https://github.com/scikit-learn/scikit-learn/blob/102e5daf66759cf896beeee229d1bf7c80ab2ba4/sklearn/model_selection/_validation.py#L792-L872): slice train/test separately, fit on train, then score the fitted estimator on test. Callback/error branches are included in the read scope; broader metadata routing is not analyzed.
- [`pipeline.py`, `_fit`, lines 519-578](https://github.com/scikit-learn/scikit-learn/blob/102e5daf66759cf896beeee229d1bf7c80ab2ba4/sklearn/pipeline.py#L519-L578), [final estimator fit, lines 630-658](https://github.com/scikit-learn/scikit-learn/blob/102e5daf66759cf896beeee229d1bf7c80ab2ba4/sklearn/pipeline.py#L630-L658), and [predict, lines 793-811](https://github.com/scikit-learn/scikit-learn/blob/102e5daf66759cf896beeee229d1bf7c80ab2ba4/sklearn/pipeline.py#L793-L811): fit intermediate transforms on supplied training data, fit the final estimator on transformed train, and later transform/predict without calling fit in that prediction path.

**Verified from source:** the dispatch passes separate indices and calls `clone(base_estimator)` per candidate/split; the fit/score path uses the training slice to fit and the other slice to score; Pipeline's inspected prediction path calls transform then predict. **Design inference:** placing learned preprocessing inside that fitted object reduces manual opportunities to cross the boundary. It does not certify correct feature timestamps, group independence, labels, splitter choice or a custom estimator's behavior.

“Test” inside `_fit_and_score` means the held-out fold for that evaluation task. During parameter search those fold scores choose candidates, so they serve a validation role. They are not an untouched final test for the entire search. For an unfamiliar term: K-fold evaluation rotates which of K partitions is held out while the others fit; it checks multiple training/validation tasks. A customer-based splitter must keep each customer wholly on one side of each task. Our lab uses one fixed three-way split, not cross-validation or sklearn execution.

Trace one candidate on one split, and explain why wrapping a classifier in Pipeline does not repair a feature matrix already selected using all labels.

<details>
<summary>Answer</summary>

| Step | Data/state | What happens |
|---|---|---|
| Dispatch | Parameter choice and split indices | A clone receives this task's parameters |
| Slice | Separate training and held-out rows | `_safe_split` prepares the two inputs |
| Pipeline fit | Training inputs/labels | Intermediate transforms fit; final estimator fits on transformed train |
| Score | Held-out inputs/labels | Prediction uses fitted transforms; the scorer compares predictions with labels |
| Search aggregation | Scores from candidate/split tasks | These scores influence selection, so a separate final audit is still needed |

If the input matrix was feature-selected using all labels beforehand, the clone receives that already contaminated representation. Pipeline cannot infer its history or undo it. Likewise, row IDs that differ do not reveal that customer groups overlap unless the chosen splitter/guards use group metadata. The code path implements a boundary provided by the caller; it is not a universal leakage detector.

</details>


### Apply the decision to an ASP.NET/Azure support project

At intake, persist ticket ID, customer ID, feature timestamp, feature-definition version and model version. Build a historical snapshot using only values that existed then. Collect late/on-time labels after the declared window, including tickets whose outcomes were missing or delayed under an explicit policy. Randomly splitting retries of one ticket is not holding out new evidence; SQL COUNT and a correct transaction cannot repair feature timing.

For an unseen-customer target, reserve whole customers. For future tickets from known customers, a chronological split with the right label/feature cutoff may be more appropriate; customer overlap is not automatically a defect for that different target. State the target before splitting. If time drift is important, a customer-disjoint split alone does not test it.

Store the fitted rule/preprocessing and score audit with their versions. An Angular dashboard can show counts, precision, recall and cost rather than a lone accuracy badge. This is an instructor design proposal, not tested ML.NET/SQL Server/Azure integration. Our tiny threshold family does not implement a production feature store, missing-outcome handling or a causal escalation policy.

Lunch - 30 minutes to eat and rest.

## 5. Lab: freeze a model and challenge its audit

**Lab · 75 minutes.** Implement the threshold search/count loop, run the independent checks and repair one defect. **Done when:** your code selects cutoff 5 from validation, matches the oracle and explains why test accuracy can fall despite correct fitting.

Build `Fit`, `Count`, `Select` and customer-disjoint guards under section 2's contract. Inputs contain 1-10000 rows per set, unique nonempty row IDs, nonempty customer IDs and scores 0-9; repeated customers within one partition are allowed. Costs are integers 1-1000; thresholds are 0-10. Reject empty/invalid inputs. Do not use test rows to construct candidates or choose the winner. Prediction consumes the score, not the future label.

Reconstruct the files below or extract the ZIP. Stop setup after 15 minutes if the exact SDK is unavailable; use the trace, search table and oracle as the reading route. Produce the demo, correctness checks and a short error explanation.

<details>
<summary>Answer - complete runnable lab</summary>

Use **.NET SDK 10.0.401**, runtime **Microsoft.NETCore.App 10.0.12**, `net10.0`, with SDK/runtime roll-forward disabled. There are no external NuGet dependencies, so no third-party transitive package lock is needed. Installing the SDK/reference packs or the first restore may need network access. After a successful restore, the `--no-restore` runs below require no network, database or Python.

All paths below are relative to `dotnet`. The ZIP has that top-level directory. If creating files manually, make that directory and every file shown here. Run commands **inside `dotnet`**; `cd dotnet` assumes its parent is your current directory.

`global.json`:

<!-- lab-file: global.json -->
```json
{
  "sdk": { "version": "10.0.401", "rollForward": "disable" }
}
```

`LessonLab/LessonLab.csproj`:

<!-- lab-file: LessonLab/LessonLab.csproj -->
```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net10.0</TargetFramework>
    <RuntimeFrameworkVersion>10.0.12</RuntimeFrameworkVersion>
    <RollForward>Disable</RollForward>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
    <TreatWarningsAsErrors>true</TreatWarningsAsErrors>
  </PropertyGroup>
</Project>
```

`LessonLab/Checks.cs`:

<!-- lab-file: LessonLab/Checks.cs -->
```csharp
public static class Checks
{
    static void Require(bool condition) { if (!condition) throw new Exception("Check failed."); }
    static void Reject(Action action)
    {
        try { action(); } catch (ArgumentException) { return; }
        throw new Exception("Expected rejection.");
    }
    // Independent 2x2 table indexed by actual and prediction; no Count call.
    static Matrix Oracle(Ticket[] rows, Rule rule)
    {
        var cells = new long[2, 2];
        foreach (var x in rows) cells[x.Late ? 1 : 0, x.Risk >= rule.Threshold ? 1 : 0]++;
        return new(cells[1, 1], cells[0, 1], cells[1, 0], cells[0, 0]);
    }
    public static void Run()
    {
        int fits = 0;
        // All ordered datasets of length 1-4, risks 0-2, labels 0/1.
        for (int n = 1; n <= 4; n++)
        for (int code = 0; code < (int)Math.Pow(6, n); code++)
        {
            int state = code;
            var rows = new Ticket[n];
            for (int i = 0; i < n; i++)
            {
                int value = state % 6; state /= 6;
                rows[i] = new($"id{i}", $"group{i}", value / 2, value % 2 == 1);
            }
            foreach (int missedCost in new[] { 1, 4 })
            {
                // Reverse enumeration, direct per-row loss; no Fit/Count/Cost.
                int expected = -1; long minimum = long.MaxValue;
                for (int t = 10; t >= 0; t--)
                {
                    long loss = rows.Sum(x => x.Risk >= t
                        ? (x.Late ? 0L : 1L) : (x.Late ? missedCost : 0L));
                    if (loss < minimum) { minimum = loss; expected = t; }
                    var rule = new Rule("oracle", t);
                    Require(Evaluation.Count(rows, rule) == Oracle(rows, rule));
                }
                Require(Evaluation.Fit(rows, missedCost).Threshold == expected);
                fits++;
            }
        }
        var sets = Data.Split(); Evaluation.Disjoint(sets);
        var candidates = Evaluation.Candidates(sets[0]);
        Require(candidates.Select(x => x.Threshold).SequenceEqual(new[] { 10, 7, 8, 5 }));
        var selected = Evaluation.Select(candidates, sets[1], 4);
        Require(selected.Threshold == 5);
        Require(Evaluation.Count(sets[2], selected) == new Matrix(2, 3, 1, 4));
        Require(Evaluation.Count(sets[2], candidates[0]).Precision is null);
        Require(Evaluation.Count([new("z", "Z", 9, false)], new("zero", 10)).Recall is null);
        Require(Evaluation.Majority([new("a", "A", 0, true), new("b", "B", 9, false)]).Threshold == 10);
        Require(Evaluation.Select([new("first", 10), new("second", 10)], sets[1], 4).Name == "first");
        var flippedTest = sets[2].Select(x => x with { Late = !x.Late }).ToArray();
        Evaluation.Disjoint(sets[0], sets[1], flippedTest);
        Require(Evaluation.Select(candidates, sets[1], 4) == selected);
        // Risk 0/9 and all labels also exercise full-domain boundaries.
        foreach (int risk in new[] { 0, 9 }) foreach (bool y in new[] { false, true })
            Require(Evaluation.Fit([new("edge", "edge", risk, y)], 4).Threshold == (y ? risk : 10));
        Reject(() => Evaluation.Fit([], 4));
        Reject(() => Evaluation.Fit(sets[0], 0));
        Reject(() => Evaluation.Count([new("bad", "G", 10, false)], selected));
        Reject(() => Evaluation.Count([new("bad", "G", 0, false)], new("bad", 11)));
        Reject(() => Evaluation.Count([new("x", "G", 0, false), new("x", "H", 1, true)], selected));
        Reject(() => Evaluation.Disjoint(sets[0], [sets[0][0] with { Id = "other" }]));
        Reject(() => Evaluation.Disjoint(sets[0], [sets[0][0] with { Group = "other" }]));
        Console.WriteLine($"PASS: {fits} fits; independent confusion tables; split/tie/boundary guards.");
    }
}
```

`LessonLab/Data.cs`:

<!-- lab-file: LessonLab/Data.cs -->
```csharp
public static class Data
{
    public static Ticket[][] Split()
    {
        var train = Enumerable.Range(0, 20).Select(i =>
        {
            int risk = i / 2;
            bool late = risk >= 8 || (risk >= 5 && i % 2 == 0);
            return new Ticket($"tr{i}", $"train-customer-{risk}", risk, late);
        }).ToArray();
        var validation = Enumerable.Range(0, 10).Select(i =>
            new Ticket($"va{i}", $"validation-customer-{i}", i, i >= 6)).ToArray();
        var test = Enumerable.Range(0, 10).Select(i =>
            new Ticket($"te{i}", $"test-customer-{i}", i, i is 4 or 7 or 9)).ToArray();
        return [train, validation, test];
    }
}
```

`LessonLab/Evaluation.cs`:

<!-- lab-file: LessonLab/Evaluation.cs -->
```csharp
// Original teaching code, MIT. Not adapted from scikit-learn.
public sealed record Ticket(string Id, string Group, int Risk, bool Late);
public sealed record Rule(string Name, int Threshold)
{
    public bool Predict(int risk) => risk >= Threshold;
}
public readonly record struct Matrix(long TP, long FP, long FN, long TN)
{
    public long N => TP + FP + FN + TN;
    public double Accuracy => (double)(TP + TN) / N;
    public double? Precision => TP + FP == 0 ? null : (double)TP / (TP + FP);
    public double? Recall => TP + FN == 0 ? null : (double)TP / (TP + FN);
    public long Cost(int missedCost) => checked(FP + missedCost * FN);
}
public static class Evaluation
{
    public static void Validate(Ticket[] rows)
    {
        if (rows.Length is < 1 or > 10000)
            throw new ArgumentException("Require 1-10000 rows.");
        var ids = new HashSet<string>(StringComparer.Ordinal);
        foreach (var row in rows)
            if (row is null || string.IsNullOrWhiteSpace(row.Id)
                || string.IsNullOrWhiteSpace(row.Group) || row.Risk is < 0 or > 9
                || !ids.Add(row.Id))
                throw new ArgumentException("Require unique IDs, nonempty groups and risk 0-9.");
    }
    public static void Disjoint(params Ticket[][] sets)
    {
        var ids = new HashSet<string>(StringComparer.Ordinal);
        var groups = new HashSet<string>(StringComparer.Ordinal);
        foreach (var set in sets)
        {
            Validate(set);
            var localGroups = set.Select(x => x.Group).Distinct(StringComparer.Ordinal);
            if (set.Any(x => !ids.Add(x.Id)) || localGroups.Any(x => !groups.Add(x)))
                throw new ArgumentException("Overlapping row IDs or customer groups.");
        }
    }
    public static Matrix Count(Ticket[] rows, Rule rule)
    {
        Validate(rows);
        if (rule.Threshold is < 0 or > 10) throw new ArgumentException("Threshold 0-10.");
        long tp = 0, fp = 0, fn = 0, tn = 0;
        foreach (var row in rows)
        {
            bool prediction = rule.Predict(row.Risk);
            if (prediction && row.Late) tp++;
            else if (prediction) fp++;
            else if (row.Late) fn++;
            else tn++;
        }
        return new Matrix(tp, fp, fn, tn);
    }
    public static Rule Majority(Ticket[] train)
    {
        Validate(train);
        return new Rule("majority", train.Count(x => x.Late) > train.Length / 2 ? 0 : 10);
    }
    public static Rule Fit(Ticket[] train, int missedCost)
    {
        Validate(train);
        if (missedCost is < 1 or > 1000) throw new ArgumentException("FN cost 1-1000.");
        var best = new Rule($"fit-FN{missedCost}", 0);
        long bestCost = long.MaxValue;
        for (int threshold = 0; threshold <= 10; threshold++)
        {
            var candidate = new Rule(best.Name, threshold);
            long cost = Count(train, candidate).Cost(missedCost);
            // Ascending candidates plus <= implements largest-threshold ties.
            if (cost <= bestCost) { best = candidate; bestCost = cost; }
        }
        return best;
    }
    public static Rule Select(Rule[] candidates, Ticket[] validation, int missedCost)
    {
        Validate(validation);
        if (candidates.Length == 0 || missedCost is < 1 or > 1000)
            throw new ArgumentException("Require candidates and FN cost 1-1000.");
        return candidates.OrderBy(r => Count(validation, r).Cost(missedCost)).First();
    }
    public static Rule[] Candidates(Ticket[] train) =>
        [Majority(train), new Rule("fixed-rule", 7), Fit(train, 1), Fit(train, 4)];
}
```

`LessonLab/Experiment.cs`:

<!-- lab-file: LessonLab/Experiment.cs -->
```csharp
public static class Experiment
{
    public static void Run()
    {
        var sets = Data.Split();
        Evaluation.Disjoint(sets);
        var clean = Evaluation.Fit(sets[0], 4);
        var cleanResult = Evaluation.Count(sets[2], clean);
        // Deliberately invalid: Late is only known after the outcome window.
        var leaked = sets.Select(s => s.Select(x => x with
            { Risk = x.Late ? 9 : 0 }).ToArray()).ToArray();
        var invalid = Evaluation.Fit(leaked[0], 4);
        var invalidResult = Evaluation.Count(leaked[2], invalid);
        Console.WriteLine($"Feature availability: clean accuracy={cleanResult.Accuracy:F3} cost={cleanResult.Cost(4)}; leaked accuracy={invalidResult.Accuracy:F3} cost={invalidResult.Cost(4)}");

        // Same four held-out customers, four training rows and balanced labels.
        var target = Enumerable.Range(4, 4).Select(i =>
            new Ticket($"new-{i}", $"c{i}", 0, i % 2 == 1)).ToArray();
        var proper = Enumerable.Range(0, 4).Select(i =>
            new Ticket($"old-{i}", $"c{i}", 0, i % 2 == 1)).ToArray();
        var overlap = target.Select(x => x with { Id = "prior-" + x.Id }).ToArray();
        Evaluation.Disjoint(proper, target);
        double Score(Ticket[] train)
        {
            var learned = train.ToDictionary(x => x.Group, x => x.Late, StringComparer.Ordinal);
            int correct = target.Count(x =>
                (learned.TryGetValue(x.Group, out bool y) && y) == x.Late);
            return (double)correct / target.Length;
        }
        Console.WriteLine($"Customer exposure: disjoint accuracy={Score(proper):F3}; overlap accuracy={Score(overlap):F3}");
        try { Evaluation.Disjoint(overlap, target); }
        catch (ArgumentException) { Console.WriteLine("Group guard rejects overlap despite unique row IDs."); }
    }
}
```

`LessonLab/Program.cs`:

<!-- lab-file: LessonLab/Program.cs -->
```csharp
using System.Globalization;
CultureInfo.CurrentCulture = CultureInfo.InvariantCulture;
if (args is ["--check"]) Checks.Run();
else if (args is ["--experiment"]) Experiment.Run();
else if (args is ["--transfer"]) Transfer.Run();
else if (args.Length == 0)
{
    var sets = Data.Split();
    Evaluation.Disjoint(sets);
    var candidates = Evaluation.Candidates(sets[0]);
    var winner = Evaluation.Select(candidates, sets[1], 4);
    Console.WriteLine($"Selected on validation: {winner.Name}, threshold={winner.Threshold}");
    foreach (var rule in candidates)
    {
        var m = Evaluation.Count(sets[2], rule);
        string precision = m.Precision?.ToString("F3") ?? "undefined";
        string recall = m.Recall?.ToString("F3") ?? "undefined";
        Console.WriteLine($"{rule.Name}: t={rule.Threshold} TP={m.TP} FP={m.FP} FN={m.FN} TN={m.TN} accuracy={m.Accuracy:F3} precision={precision} recall={recall} cost={m.Cost(4)}");
    }
}
else throw new ArgumentException("Use no args, --check, --experiment or --transfer.");
```

`LessonLab/Transfer.cs`:

<!-- lab-file: LessonLab/Transfer.cs -->
```csharp
public static class Transfer
{
    public static void Run()
    {
        // One customer contributes four errors; another contributes one success.
        Ticket[] rows = [new("a1", "A", 0, true), new("a2", "A", 0, true),
            new("a3", "A", 0, true), new("a4", "A", 0, true), new("b1", "B", 0, false)];
        var rule = new Rule("never-alert", 10);
        var rowMatrix = Evaluation.Count(rows, rule);
        double macroCost = rows.GroupBy(x => x.Group).Average(g =>
            (double)Evaluation.Count(g.ToArray(), rule).Cost(4) / g.Count());
        if (rowMatrix.Cost(4) != 16 || Math.Abs(macroCost - 2) > 1e-12)
            throw new InvalidOperationException("Wrong unit weighting.");
        Console.WriteLine($"Row mean cost={(double)rowMatrix.Cost(4) / rows.Length:F3}; equal-customer mean cost={macroCost:F3}");
    }
}
```

```bash
cd dotnet
dotnet --version
dotnet restore LessonLab
dotnet run --no-restore -c Release --project LessonLab
dotnet run --no-restore -c Release --project LessonLab -- --check
dotnet run --no-restore -c Release --project LessonLab -- --experiment
dotnet run --no-restore -c Release --project LessonLab -- --transfer
```

Expected SDK output is `10.0.401`. The following deterministic demo/check outputs were observed with the pinned environment:

```text
Selected on validation: fit-FN4, threshold=5
majority: t=10 TP=0 FP=0 FN=3 TN=7 accuracy=0.700 precision=undefined recall=0.000 cost=12
fixed-rule: t=7 TP=2 FP=1 FN=1 TN=6 accuracy=0.800 precision=0.667 recall=0.667 cost=5
fit-FN1: t=8 TP=1 FP=1 FN=2 TN=6 accuracy=0.700 precision=0.500 recall=0.333 cost=9
fit-FN4: t=5 TP=2 FP=3 FN=1 TN=4 accuracy=0.600 precision=0.400 recall=0.667 cost=7
```

```text
PASS: 3108 fits; independent confusion tables; split/tie/boundary guards.
```

The majority and fixed-rule baselines were prespecified, and all four candidates were frozen before test reporting. Reporting those comparisons is permitted by this illustrative protocol; selecting a replacement winner from their test results is not. Here cutoff 7 has lower test cost than the selected cutoff 5. That discrepancy is deliberately visible: validation selection does not guarantee the best realized test score. Do not silently switch to cutoff 7 and call the same test untouched evidence.

On test, the selected model's FN is score 4 and FPs are 5,6,8. Training associates larger scores with lateness, while this small test has a late ticket at 4 and on-time tickets at 5,6,8. That error pattern suggests testing feature adequacy and distribution change using new development data; the fixture cannot identify their production cause. No claim that training/test were IID is made.

`Checks` exhausts all 1-4-row ordered datasets with scores 0-2 and binary labels: 1554 datasets, two loss settings, 3108 fits. Its oracle uses reverse cutoff enumeration and direct row loss, not `Fit`, `Count` or `Matrix.Cost`. A separate 2x2 cell table checks all eleven thresholds for each dataset/loss setting. Both share the input representation, score comparison and finite threshold family. Full-domain 0/9 cases, undefined ratios, majority/selection ties, overlapping IDs/groups and invalid scores/costs add boundary checks. The fixed demo's selection/test cells are asserted.

The code signature of `Select` has no test parameter. A changed-test-label witness checks that the same train/validation selection remains fixed; it is not a universal noninterference proof for every external data-preparation pipeline. Exhaustive small cases do not cover arbitrary long IDs, every dataset size or real label errors. The invariant argument establishes finite-search correctness; no checker proves generalization or production usefulness.

If a pin is missing, install the exact version or use the reading route. An overlap exception requires rebuilding the intended partitions, not removing the guard. A score-10 exception means the feature domain changed; revise the contract and candidate family deliberately rather than clipping silently. A source-only ZIP and [lab guide](../../labs/honest-evaluation/dotnet/README.md) supplement this complete solution.

</details>

A developer changes the fit update from `cost <= bestCost` to `cost < bestCost`. What changes under the declared contract?

<details>
<summary>Answer</summary>

Ascending enumeration with `<` retains the first minimizer, so c=1 picks cutoff 5 instead of 8. It is still an empirical minimizer but violates the specified largest-threshold tie policy, which prefers fewer flags on tied loss. The reverse-enumeration oracle retains 8 and catches this defect. Restore `<=`, or explicitly revise the policy and all expected results; do not treat an arbitrary tie as impossible.

</details>


A developer concatenates validation and test before calling `Select`, while `Fit` still uses train only. Is this evaluation honest?

<details>
<summary>Answer</summary>

No. Candidate choice now depends on final test labels even though parameter fitting did not. In this fixture the combined costs are 28,9,17,8 and still select cutoff 5; an unchanged winner does not make the information use valid. A held-out boundary covers feature decisions, preprocessing, thresholds and candidate selection, not just the method named Fit. Keep selection on validation and audit a frozen choice on test. If test has already guided revision, use fresh untouched evidence for the revised procedure; renaming the old rows does not restore independence.

</details>


Pause - 10 minutes away from the screen.

## 6. Controlled experiments: a score can improve for the wrong reason

**Experiment · 45 minutes.** Run two one-factor witnesses and record assumptions, prediction, observation and inference separately. **Done when:** you can reproduce both outputs and state what neither result establishes.

### Experiment A: change feature availability

Assume the decision occurs at intake and `Late` becomes known only after 24 hours. Predict that copying the label into the score will make this particular fixture perfectly separable. Change only the feature definition from supplied intake score to `Late ? 9 : 0`; keep rows, labels, partitions, cutoff family, fitting loss and algorithm fixed. Fit each representation on train with c=4 and audit its frozen result on the same test. This isolates representation contamination rather than adaptively selecting a new model on test.

Run `dotnet run --no-restore -c Release --project LessonLab -- --experiment` inside `dotnet`. Explain the feature comparison and whether 100% supports deployment.

<details>
<summary>Answer - observed feature witness</summary>

```text
Feature availability: clean accuracy=0.600 cost=7; leaked accuracy=1.000 cost=0
```

**Observation:** the supplied-feature cutoff is 5 with cost 7; label-derived features permit cutoff 9 with no mistakes. **Inference:** the perfect score measures future-outcome information, unavailable to the stated intake predictor. It does not show better learning or savings. A random/disjoint row split cannot repair this within-row leak.

**Limits:** labels/features are constructed and deterministic; no real ingestion clock, label delay, noisy outcomes or outage was tested. This is a counterexample to score-based trust, not an estimate of leakage magnitude in production. Availability must be reviewed semantically because both representations satisfy the numeric score validator. The code's deliberate misuse is marked as invalid and is never a deployable candidate.

</details>


### Experiment B: change exposure to the target customers

Assume the target is unseen customers and a customer has a fixed binary outcome in this witness. Four held-out customers c4-c7 each have one new row, with two late and two on-time outcomes. A memorizer stores training customer labels and predicts 0 for unknown customers. Compare four training rows from c0-c3 against four earlier rows from c4-c7. Both training sets have the same size, dummy score and class balance; held-out rows, labels, fallback and memorizer are fixed. Change whether the target customers were already exposed.

Predict the two accuracies and inspect the group guard. Does rejecting overlapping row IDs alone detect the problem?

<details>
<summary>Answer - observed customer witness</summary>

```text
Customer exposure: disjoint accuracy=0.500; overlap accuracy=1.000
Group guard rejects overlap despite unique row IDs.
```

**Observation:** unknown customers receive constant 0, correct for two of four; exposed customers are looked up correctly for all four. Training/test row IDs differ in both paths, but customer IDs overlap in the invalid path. **Inference:** for the unseen-customer claim, the apparent gain comes from prior customer exposure, not improved behavior on new customers. The main lab's group guard rejects that exposure.

**Limits:** customer labels are constant by construction, the sample is balanced and tiny, and the memorizer is a different model from the threshold lab. This second witness does not measure the threshold model's leakage sensitivity. No independence, temporal drift, realistic customer effects or future known-customer performance is established. Customer overlap may be appropriate for a properly timed known-customer target; it invalidates the particular unseen-customer target stated here.

No timing measurements are reported. The observations are exact counts from synthetic witnesses, not confidence estimates or universal performance comparisons.

</details>


Pause - 10 minutes away from the screen.

## 7. Transfer: change whose errors count equally

**Transfer · 35 minutes.** Replace equal-ticket loss with equal-customer loss and check a duplicate-volume variation. **Done when:** your formula identifies the target unit and remains unchanged when one customer's identical rows are repeated.

Customer A has four late tickets, customer B one on-time ticket; all scores are 0. Use the never-flag rule, c=4. The business now asks for the average customer's mean ticket cost rather than the average ticket's cost. Derive both summaries, implement the new aggregation using the supplied `Transfer.Run`, and explain why a single global confusion matrix no longer determines the equal-customer result.

<details>
<summary>Answer</summary>

A's total cost is 16, mean ticket cost 4; B's total/mean cost is 0. The ticket-weighted mean is 16/5=3.2. The equal-customer mean is `(4+0)/2=2`. For G customers, compute `sum_g (loss_g / n_g) / G`, keeping customer counts and costs separately. A global table loses which customer contributed each error.

`Transfer.Run` groups rows, calls the same counting rule within each group, divides by that group's row count and averages those group means. It asserts total cost 16 and equal-customer mean 2. Run inside `dotnet`:

```bash
dotnet run --no-restore -c Release --project LessonLab -- --transfer
```

Observed output:

```text
Row mean cost=3.200; equal-customer mean cost=2.000
```

Repeating all of A's identical rows doubles its numerator and denominator, so its mean stays 4 and the equal-customer mean stays 2. The ticket mean becomes 32/9, about 3.556. This invariance holds for proportionally repeating a customer's full set, not selectively repeating only its errors.

This changes the target quantity and weights, not just variable names. Recall Lesson 08: equal pair weights were justified by equal pair sizes; unequal groups need a declared weighting target. If the deployment goal is equal customers, fitting/validation should also use that objective when comparing policies. Merely changing a final dashboard after selecting on row loss does not optimize customer loss. This extension aggregates fixed predictions; it does not refit an equal-customer model or guarantee fairness to every customer.

</details>


## 8. Synthesize a defensible release decision

**Synthesis · 45 minutes.** Answer the four prompts separately, then write a short decision memo. **Done when:** the memo states target, available features, selected rule, evidence, uncertainty and the next test that could change the decision.

Can the selected threshold be called correct even though the fixed-rule baseline has lower test cost?

<details>
<summary>Answer</summary>

Its training search and validation selection can be correct under their contracts while its test performance is worse than a baseline. Algorithmic correctness, empirical optimality and usefulness on future observations are different claims. Report the result rather than selecting a new winner from the audit. Gather new development/audit evidence under a declared revised protocol before a production recommendation.

</details>


Would a Wilson interval on test accuracy repair leakage or prove the model's intervention works?

<details>
<summary>Answer</summary>

No. For a frozen predictor and appropriate IID binary correctness outcomes, the Wilson calculation from Lesson 07 can describe uncertainty in an accuracy proportion, with its finite-coverage limitation. It does not remove test-driven selection, unavailable features, linked customer outcomes or distribution drift. Weighted cost is not a Bernoulli proportion. Predictive uncertainty also does not identify the causal effect of escalating a ticket; that needs an appropriate intervention design from Lesson 08.

</details>


Does score 7 mean a 70% chance of lateness, and does this lab verify calibration?

<details>
<summary>Answer</summary>

No. It is an arbitrary ordinal intake feature with a declared domain. The threshold model returns a binary decision, not an estimated probability. Calibration concerns whether predicted probabilities match outcome frequencies under a stated evaluation design; no probability estimator or calibration test was implemented. Dividing a feature by 10 does not turn it into a verified probability.

</details>


What release memo follows from the observed fixture?

<details>
<summary>Answer</summary>

Target: tickets from unseen customers, predicted at intake with a 24-hour outcome window. Available input: versioned intake score, not future lateness. Protocol: customer-disjoint train/validation/test; fit on train, select on validation using FP+4*FN and freeze before test. Selected cutoff: 5. Evidence: test TP/FP/FN/TN=2/3/1/4, cost 7 versus majority 12 and prespecified cutoff-7 baseline 5. This small synthetic fixture supports an executable evaluation protocol, not a release or savings claim.

Unknowns: representative customers/time, labels/missing outcomes, feature availability, costs/capacity and stability. Next question: on new dated development data, does the same prespecified procedure reduce declared customer/ticket loss compared with the fixed rule? Reserve new untouched audit data and review timing/group boundaries before that comparison. A causal rollout question about escalation's effect is separate.

</details>


The revised model is small but complete: learning searches a declared rule family, evaluation protects an information boundary, and the unit/loss determine what the score means. Remaining directions include richer models, temporal splits, learned preprocessing and nested evaluation. None is required to claim universal model quality today.

## Sources and reuse

- scikit-learn documentation and implementation at the commit linked above support metric definitions, preprocessing boundaries and the inspected evaluation path. [BSD-3-Clause license](https://github.com/scikit-learn/scikit-learn/blob/102e5daf66759cf896beeee229d1bf7c80ab2ba4/COPYING). Source snippets are not redistributed; all C# code is original teaching code.
- [Lesson 07](../2026-10-11-sampling-uncertainty/lesson.md) supports the expectation/uncertainty bridge; [Lesson 08](../2026-10-12-experimental-design/lesson.md) bounds causal claims and unit weighting.
- Original lesson prose: CC BY 4.0. Original lab code: MIT; the ZIP includes its license.

<!-- LESSON_NAVIGATION_START -->
## Related reading

- [Lesson 08 - Experimental design: a difference is not yet a causal effect](../2026-10-12-experimental-design/lesson.md) - Separate predictive evaluation from an intervention claim.
- [Lesson 07 - Sampling uncertainty: more records need not mean more evidence](../2026-10-11-sampling-uncertainty/lesson.md) - Revisit observation units and uncertainty assumptions.
- [C# lab guide](../../labs/honest-evaluation/dotnet/README.md) - Pinned setup, oracle checks and synthetic experiment limits.

---

[← Previous: Lesson 08 - Experimental design: a difference is not yet a causal effect](../2026-10-12-experimental-design/lesson.md) · [All lessons](../../README.md)
<!-- LESSON_NAVIGATION_END -->
