# Lesson 08 - Experimental design: a difference is not yet a causal effect

[Tiếng Việt](../../vi/lessons/2026-10-12-experimental-design/lesson.md) · [Download the C# lab](https://nguyenan97.github.io/computer-science-learning-agent/labs/experimental-design/dotnet-lab.zip)

A .NET team routes small requests to a new implementation and large requests to the old one. The new arm looks faster even when it changes nothing. Today we hold the workload fixed, change the assignment rule and distinguish a measured contrast from a causal effect.

**Goal:** design a controlled comparison, prove what its estimator targets, report randomization uncertainty and bound a causal claim. The planner selects experimental design after sampling uncertainty. We reuse expectation, variance, independent checks and half-open ranges. Potential outcomes, confounding, randomized pairs and a sharp-null randomization test are introduced here.

## Core ideas

- **An effect compares the same unit under two actions.** A request might take 10 with the old implementation and 6 with the new one. Its effect is -4, but a live request exposes only the outcome under the action it receives.
- **A comparison needs a design.** Comparing small new-arm requests with large old-arm requests mixes implementation and request size. Random assignment makes allocation independent of the fixed potential outcomes under the stated design; one realized allocation can still be unbalanced.
- **Pairing controls a known source of variation.** Match two comparable units before assignment, then randomly treat one of each pair. This fixes one treated and one control unit per pair without requiring their outcomes to be equal.
- **Uncertainty concerns alternative assignments.** The same fixed cohort can produce different contrasts when assignment changes. Enumerating a small design shows that spread; it does not sample future traffic.

Use the trace, source ledger and complete worked code as a reading-only route. Bound lab setup to 15 minutes of its block. All outcomes below are synthetic integer values labelled milliseconds; no service latency is timed.

## 1. Recall and define the comparison

**Recall · 20 minutes.** Reconstruct the three planner-selected answers, then separate a correct computation from a justified comparison. **Done when:** you can name the model boundary of each answer and the missing design information in a before/after chart.

1. From Lesson 07: what does nominal 95% confidence mean for a Wilson interval?

<details>
<summary>Answer</summary>

Before sampling, random intervals aim to cover a fixed p in about 95% of repeated model samples. Wilson finite coverage can differ; this is not posterior probability 0.95 for the observed interval or a guarantee about biased/dependent data.

</details>

2. From Lesson 05: does `(Tenant,Occurred,Amount)` both cover totals and guarantee page order by `(Occurred,Id)`?

<details>
<summary>Answer</summary>

It covers COUNT/SUM(Amount) under tenant/time predicates, but Amount breaks equal-time ties before rowid. To meet that page order, keep ORDER BY and consider (Tenant,Occurred,Id,Amount); SQL Server can keep Amount as an included nonkey column.

</details>

3. From Lesson 01: which assumptions support expected linear deduplication, and why does a benchmark not prove service p99?

<details>
<summary>Answer</summary>

Bounded key hash/equality cost, adequate hash distribution and amortized resizing support expected O(n); adversarial collisions can increase comparisons. A synthetic benchmark measures its chosen workload and environment, not production queues, key distributions, peak memory or request latency.

</details>


A correct query can retrieve the wrong comparison cohort. A faster synthetic benchmark does not establish a production effect. A Wilson interval describes a proportion under its model; it cannot repair a deployment that sends different workloads to different arms. Today the next question is how the arms were created.

## 2. Build the causal question before calculating

**Foundation · 50 minutes.** Annotate the six-pair trace, derive its expectation and state the assignment invariant. **Done when:** you can explain why the estimate can miss the true effect in one allocation while being correct in expectation over the design.

### One unit, two potential outcomes

Suppose unit u0 would produce 10 under control and 6 under treatment; u1 would produce 14 and 10. Giving treatment to u0 observes 6, while giving control to u1 observes 14. The contrast is -8, although each unit's effect is -4. Swapping assignment produces 10-10=0. Averaging the two equally likely contrasts gives -4.

Now write `Y_i(0)` and `Y_i(1)` for unit i's fixed potential outcomes under the two precisely specified actions. Let `Z_i` be 0 or 1 for its assignment. The observed outcome is `Y_i = Y_i(Z_i)` under consistency: the action actually delivered is the defined action. The target for this fixed cohort of N units is:

```text
tau = (1/N) * sum_i [Y_i(1) - Y_i(0)]
```

We assume no unit's outcome changes because another unit is treated. A shared queue, shared cache or capacity-limited database can violate this no-interference assumption. Both versions, the outcome window, eligible units and outcome collection must be specified. One request cannot generally reveal both outcomes at once; replaying it later also changes time/cache state. Only the simulator makes both potential outcomes available to the oracle.

Random assignment and random sampling answer different questions. Assignment supports comparison of actions within this cohort. Sampling supports generalization to a specified population. Randomizing twelve convenient units does not make them representative of future production.

### An invariant and a narrated trace

Make B=6 pairs from twelve units using pretreatment information. In every pair, a fair independent assignment chooses which unit gets treatment; the other gets control. Exactly one treated and one control unit per pair is the invariant. There are `2^B=64` equally likely allocations in this mathematical design. Our program enumerates them all; it does not generate a random allocation using a production RNG.

The fixed baselines are `[10,14,20,28,40,52,60,76,80,100,120,144]`; treatment subtracts 4 for every unit. Pair adjacent values. Mask 21 is an example chosen in the code, not a random draw: bit b=1 treats the left unit of pair b. Complete the trace and running sum of treatment-minus-control differences.

<details>
<summary>Answer</summary>

| Pair | Baselines left/right | Treated side | Left seen | Right seen | d_b | Running sum |
|---|---|---|---|---|---|---|
| 0 | 10/14 | Left | 6 | 14 | -8 | -8 |
| 1 | 20/28 | Right | 20 | 24 | 4 | -4 |
| 2 | 40/52 | Left | 36 | 52 | -16 | -20 |
| 3 | 60/76 | Right | 60 | 72 | 12 | -8 |
| 4 | 80/100 | Left | 76 | 100 | -24 | -32 |
| 5 | 120/144 | Right | 120 | 140 | 20 | -12 |

Each pair contains exactly one treatment and one control. The estimate is -12/6=-2; the oracle effect is -4 because each of the twelve individual effects is -4. The estimator's accumulator equals the sum of treatment-minus-control differences over the processed prefix. Assignment orientation changes which difference to add, while preserving both invariants. The mask's set bits are 0,2,4; reading its binary notation left-to-right as pair order would reverse that meaning.

</details>


Write `d_b` for observed treatment minus control in pair b. The estimate is `D = sum_b d_b / B`. Because both arms have B units, this equals the treated mean minus the control mean. Equal pair weights target all 2B units equally; arbitrary unequal-size blocks need a different weighting argument.

### Why the estimator targets the cohort effect

For a pair with units a and c, the two possible contrasts are `Y_a(1)-Y_c(0)` and `Y_c(1)-Y_a(0)`. Each has probability 1/2. Their mean is half the sum of the two individual effects. Summing over B pairs and dividing by B gives `E_design[D]=tau`. This is an expectation over assignment with potential outcomes fixed, not a claim that the observed D equals tau. Linearity needs no outcome IID assumption. Independent fair pair assignments are needed for the uniform enumeration and for adding pair variances.

What makes the equality fail if we always treat the lighter unit? Show the zero-effect counterexample.

<details>
<summary>Answer</summary>

Always treating the left/lighter unit gives only `Y_left(1)-Y_right(0)`, not two equally weighted contrasts. With no effect, those contrasts are -4,-8,-12,-16,-20,-24, averaging -14 while tau=0. Both arms still contain six units, so equal counts alone do not fix confounding. Randomization removes this systematic selection in expectation; it does not force one example contrast to be zero.

</details>


In the constant-effect fixture, write each baseline gap as `g_b = right baseline - left baseline`. A pair contrast is `-4 + g_b` or `-4 - g_b`. Its variance is `g_b^2`. Independent pair assignments give:

```text
Var_design(D) = sum_b g_b^2 / B^2
SD_design(D)  = sqrt(sum_b g_b^2) / B
```

Here the gaps are 4,8,12,16,20,24. The SD is `sqrt(1456)/6`, about 6.3596. This is the spread of D across all allocations in the synthetic design. It is neither the SD of unit outcomes nor a standard error known from real data: real data do not expose all potential outcomes. General varying effects require the two possible contrasts per pair; the gap formula above relies on this fixture's constant effect.

Why can adding the same -4 effect change the mean without changing this SD?

<details>
<summary>Answer</summary>

Every possible D is shifted by -4, so its mean shifts by -4 and its deviation from that mean stays unchanged. The entire randomization distribution moves without changing its spread. This statement assumes a constant additive effect for all units; unequal effects need a new calculation. It says nothing about physical service noise.

</details>


Pause - 10 minutes away from the screen.

## 3. Read design assumptions and challenge a reversal

**Source reading · 45 minutes.** Read the bounded sections and fill the claim/evidence/limit ledger. **Done when:** you separate allocation from sampling, identify a confounder and qualify the statement that randomization balances groups.

Read Hernán and Robins, [Causal Inference: What If, author-hosted August 2026 version](https://miguelhernan.org/s/hernanrobins_WhatIf_19aug26.pdf): sections 1.1-1.2 (printed pages 3-6), including Fine Point 1.1 on interference; and section 2.1 (printed pages 13-16) on ideal randomization and exchangeability. We use its potential-outcome language and ideal-trial assumptions, not its later observational estimators. Exchangeability here means allocation does not select units with systematically different potential outcomes under the design, not that realized outcomes must match.

Also read OpenStax [1.4, Experimental Design and Ethics](https://openstax.org/books/introductory-statistics-2e/pages/1-4-experimental-design-and-ethics), the opening explanation through the aspirin experiment and blinding. Its treatment, experimental-unit and control-group examples explain what is varied. Qualify its broad wording about all lurking variables being spread equally: finite randomization balances in expectation, and even an ideal finite experiment has assignment variation. Blinding reduces behavior/measurement effects; it is separate from assignment.

Complete a ledger for the following three claims: random assignment identifies each unit's effect; balanced arm counts guarantee equal workload; and a cohort contrast can target an average effect under a specified design.

<details>
<summary>Answer</summary>

| Claim | Evidence | Limit |
|---|---|---|
| Each individual effect is identified | What If 1.1 observes only Y_i(Z_i) | The other potential outcome is missing; assignment alone does not reveal it |
| Equal counts imply equal workload | Six pairs guarantee six units per arm | The fixed trace still has different baseline sums; chance imbalance remains |
| The contrast targets the average effect | Two equiprobable pair orientations average the pair effects | Requires the stated assignment and consistent outcomes/no interference; generalization needs more |

The first two claims are false as stated. The third is supported by the finite-cohort derivation. The book's ideal-trial reasoning and our design expectation address comparison under assumptions; neither proves every hidden variable is exactly balanced in a finite realization.

</details>


### A confounder can reverse the aggregate comparison

A confounder helps determine both assignment and the outcome. Request size can do both when engineers deliberately route small requests to the new path. In an observational table, consider successes rather than latency:

| Workload | Control successes/total | Treatment successes/total |
|---|---|---|
| Easy | 81/90 = 90% | 19/20 = 95% |
| Hard | 1/10 = 10% | 24/80 = 30% |
| All | 82/100 = 82% | 43/100 = 43% |

Treatment has a higher observed rate within each workload but a lower aggregate rate. Explain the reversal and compute a standardized descriptive comparison with equal easy/hard weights. Does it establish causation?

<details>
<summary>Answer</summary>

Control has 90% easy units and treatment only 20%, so their aggregate rates use different weights. Equal easy/hard weighting gives control `(0.90+0.10)/2=0.50`, treatment `(0.95+0.30)/2=0.625`, a +0.125 descriptive difference or 12.5 percentage points. That standardizes one measured factor, but does not remove hidden selection, missing outcomes or other confounders. Without a justified assignment/observational identification argument, it remains an association. The target weights must be selected for a reason before choosing a favorable result.

</details>


The same issue affects before/after deploys: traffic mix, incident load and cache state can change with time. Randomizing after excluding failed telemetry, pairing on a treatment-affected metric or stopping on a favorable result changes the procedure. Fix eligibility, pairing variables, allocation probabilities, metric, outcome window, missing-data policy and stopping rule before assignment. A stable feature flag alone supplies none of these guarantees.

What changes if ten retry rows represent one originally assigned tenant rather than ten assigned tenants?

<details>
<summary>Answer</summary>

Assignment remains at tenant level; retry rows do not create new allocation decisions. Define one tenant outcome under a prespecified aggregation/window, or use an analysis that respects tenant clusters. Ten copies of a tenant outcome carry the same assignment and can also share incidents. Dedupe removes repeated IDs but cannot establish independence between tenants or remove interference.

</details>


## 4. A production assignment path in GrowthBook

**Source analysis · 45 minutes.** Trace the pinned SDK path and its range boundaries. **Done when:** you can separate verified allocation mechanics from the additional design and telemetry needed for a causal report.

GrowthBook is a feature-flag and experimentation platform. Its JavaScript SDK solves the product problem of evaluating experiment variations from an identity and configuration and reporting an exposure. Read only these slices at commit `7f0b1c3059ac634edd82b18e43ce7d92d08dbb3e`:

- [core.ts](https://github.com/growthbook/growthbook/blob/7f0b1c3059ac634edd82b18e43ce7d92d08dbb3e/packages/sdk-js/src/core.ts): `runExperiment` declaration/initial variation guard (427-447), missing hash identity (528-545), hashing/ranges/exclusion (674-730), callback dispatch (814-833); `getHashAttribute` (1073-1108), and `onExperimentViewed` (76-113).
- [util.ts](https://github.com/growthbook/growthbook/blob/7f0b1c3059ac634edd82b18e43ce7d92d08dbb3e/packages/sdk-js/src/util.ts): hash versions (19-46), half-open `inRange`/`chooseVariation` (53-75) and `getBucketRanges` (183-233).

The links pin the actual code, not the moving docs. The current [JavaScript SDK guide](https://docs.growthbook.io/lib/js), initialization and tracking callback example, supplies application context. We do not run the SDK, trace persistence/network retries or inspect the platform's statistical engine, bandits or every override/sticky-bucket path. The source is MIT outside the listed enterprise directories; our lab is original code, not an SDK port.

### What the selected path establishes

With ordinary experiment evaluation and no overriding/sticky assignment, the SDK obtains a hash identity (`id` by default), combines it with the experiment seed/key and hash version, chooses a half-open variation range, and excludes a missing identity, invalid version or bucket outside the ranges. Fixed inputs/configuration make this path deterministic. Its workload is repeated feature evaluation across application identities; the slice gives no benchmark size or throughput guarantee.

This avoids a fresh coin flip at every feature evaluation in that path, which could switch a user's variation within a visit. Stability introduces dependencies on identity, seed, hash version and range configuration. Source version 1 is explicitly retained for compatibility; version 2 is labelled unbiased in a comment. The code verifies different formulas, not empirical independence/uniformity for every real ID distribution. Uniform bucket behavior is an assumption requiring an audit of the chosen identities, not a theorem established by the comment.

For two variations with equal weights and coverage 0.8, follow `getBucketRanges` and `chooseVariation`. Which variations contain buckets 0.39,0.40,0.50,0.89,0.90? Why is coverage not the contiguous interval `[0,0.8)`?

<details>
<summary>Answer</summary>

| Bucket n | Range membership | Result |
|---|---|---|
| 0.39 | [0,0.4) | Variation 0 |
| 0.40 | Neither | Excluded (-1) |
| 0.50 | [0.5,0.9) | Variation 1 |
| 0.89 | [0.5,0.9) | Variation 1 |
| 0.90 | Neither | Excluded (-1) |

The start advances by the full weight 0.5, while each included interval has width `coverage*weight=0.4`. Thus there is a gap [0.4,0.5) and [0.9,1), total included length 0.8. `chooseVariation` scans ranges and uses an excluded upper endpoint. Under a uniform bucket model, inclusion probability is 0.8 and each variation has probability 0.4; fixed real IDs need not have those exact fractions. `coverage` here controls eligibility, not the confidence coverage of Lesson 07. This arithmetic traces the pinned formulas; it is not a run of the SDK.

</details>


### Applying the decision in a .NET/Angular/Azure project

For a checkout experiment, choose the tenant or user as assignment unit before request processing, persist or reconstruct a stable assignment under frozen configuration, and join outcomes back to that unit. An Angular display decision and a .NET service action must agree on experiment version and unit identity. Record assignment, delivered action, eligibility, exposure and outcome separately. Analyze all assigned eligible units under the prespecified outcome policy; conditioning only on those who later clicked can create selection bias. Assignment effects and effects of actually receiving the action differ when delivery is imperfect.

This is an instructor design proposal, not a verified deployment or GrowthBook .NET API. If the action changes a shared queue/cache, randomizing users may violate no interference; consider isolated resources or a cluster/time-block design, then use its assignment distribution. Our paired-unit lab does not validate those production designs.

Build a second ledger: what do hashing, missing-ID exclusion and callback deduplication verify, and which causal or delivery claims remain unsupported?

<details>
<summary>Answer</summary>

| Verified in the slice | Design inference or missing evidence |
|---|---|
| Fixed identity/seed/hash version determines a bucket in the ordinary path | Audit identity distribution and freeze configuration before claiming a suitable random allocation |
| Empty hash identity excludes the unit from experiment evaluation | Excluded identities may be a selected subgroup; this does not validate representativeness |
| `trackedExperiments`, when present, suppresses a repeated dedupe key in that user context | It does not prove durable exactly-once exposure delivery or completeness of outcomes |
| Tracking callbacks receive experiment/result/user context | A database join and the causal analysis are additional application work |

The verified mechanics enable experiment delivery. Our recommendation to align Angular/.NET identities and analyze assigned units is a design inference, not a measured integration. The local tracked set is not the durable receipt mechanism from Lesson 06.

</details>


Lunch - 30 minutes to eat and rest.

## 5. Implement the design and two independent checks

**C# lab · 75 minutes.** Run the example, inspect estimator inputs, validate the oracle and repair a sign defect. **Done when:** the trace matches, `--check` passes and you can explain which information a real estimator is allowed to see. Stop setup after 15 minutes and use the worked route if the pinned SDK is unavailable.

Create the complete lab below or extract the ZIP. Keep potential outcomes out of the observed estimator: `Observe` exposes only the received action's outcome, `Estimate` consumes `Seen[]`, and `Oracle` alone reads both outcomes. Enumerate all pair assignments, compare with a separate arm-scan oracle, and exhaust small potential-outcome tables. Run demo, checks and experiment. What can these checks establish?

<details>
<summary>Answer - complete runnable lab</summary>

Use SDK **10.0.401**, runtime **Microsoft.NETCore.App 10.0.12**, target **net10.0**; disable SDK/runtime roll-forward. No external NuGet dependencies are used; the empty lock file is still checked. The pinned SDK/reference pack must be available for the initial restore. The program uses no network/database and writes only `assignments.csv` in experiment mode.

Extract the ZIP or create `dotnet` with the files below. Run from `dotnet`; `cd dotnet` below assumes you start in its parent directory.

`global.json`:
```json
{
  "sdk": { "version": "10.0.401", "rollForward": "disable" }
}
```


`LessonLab/LessonLab.csproj`:
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
    <RestorePackagesWithLockFile>true</RestorePackagesWithLockFile>
    <RestoreLockedMode>true</RestoreLockedMode>
  </PropertyGroup>
</Project>
```


`LessonLab/packages.lock.json`:
```json
{
  "version": 1,
  "dependencies": {
    "net10.0": {}
  }
}
```

Run commands:
```bash
cd dotnet
dotnet --version
dotnet restore LessonLab --locked-mode
dotnet run --no-restore -c Release --project LessonLab
dotnet run --no-restore -c Release --project LessonLab -- --check
dotnet run --no-restore -c Release --project LessonLab -- --experiment
```


`LessonLab/Design.cs`:
```csharp
public sealed record Unit(string Id, int Y0, int Y1);
public sealed record Pair(Unit Left, Unit Right);
public sealed record Seen(string LeftId, string RightId, bool LeftTreated,
    int LeftOutcome, int RightOutcome);
public sealed record Tail(int Extreme, int Total)
{
    public double P => (double)Extreme / Total;
}

public static class Design
{
    public static void Validate(Pair[] pairs)
    {
        if (pairs.Length is < 1 or > 10)
            throw new ArgumentOutOfRangeException(nameof(pairs));
        var ids = new HashSet<string>(StringComparer.Ordinal);
        foreach (var u in pairs.SelectMany(p => new[] { p.Left, p.Right }))
            if (string.IsNullOrWhiteSpace(u.Id) || !ids.Add(u.Id) ||
                u.Y0 is < 0 or > 10000 || u.Y1 is < 0 or > 10000)
                throw new ArgumentException("Invalid unit, outcome or repeated ID.");
    }

    public static Seen[] Observe(Pair[] pairs, int mask)
    {
        Validate(pairs);
        if (mask < 0 || mask >= (1 << pairs.Length))
            throw new ArgumentOutOfRangeException(nameof(mask));
        return pairs.Select((p, b) =>
        {
            bool left = (mask & (1 << b)) != 0;
            return new Seen(p.Left.Id, p.Right.Id, left,
                left ? p.Left.Y1 : p.Left.Y0,
                left ? p.Right.Y0 : p.Right.Y1);
        }).ToArray();
    }

    public static long[] Differences(Seen[] seen)
    {
        if (seen.Length is < 1 or > 10)
            throw new ArgumentOutOfRangeException(nameof(seen));
        var ids = new HashSet<string>(StringComparer.Ordinal);
        foreach (var s in seen)
            if (string.IsNullOrWhiteSpace(s.LeftId) || !ids.Add(s.LeftId) ||
                string.IsNullOrWhiteSpace(s.RightId) || !ids.Add(s.RightId) ||
                s.LeftOutcome is < 0 or > 10000 || s.RightOutcome is < 0 or > 10000)
                throw new ArgumentException("Invalid observed record.");
        return seen.Select(s => s.LeftTreated
            ? (long)s.LeftOutcome - s.RightOutcome
            : (long)s.RightOutcome - s.LeftOutcome).ToArray();
    }

    public static double Estimate(Seen[] seen) =>
        (double)Differences(seen).Sum() / seen.Length;

    // Only a synthetic oracle can see both potential outcomes.
    public static double Oracle(Pair[] pairs)
    {
        Validate(pairs);
        return pairs.SelectMany(p => new[] { p.Left, p.Right })
            .Average(u => (double)u.Y1 - u.Y0);
    }

    public static double[] Distribution(Pair[] pairs)
    {
        Validate(pairs);
        return Enumerable.Range(0, 1 << pairs.Length)
            .Select(mask => Estimate(Observe(pairs, mask))).ToArray();
    }

    public static Tail SharpNull(Seen[] seen)
    {
        long[] d = Differences(seen);
        long observed = Math.Abs(d.Sum());
        int extreme = 0, total = 1 << d.Length;
        for (int mask = 0; mask < total; mask++)
        {
            long sum = 0;
            for (int b = 0; b < d.Length; b++)
                sum += (mask & (1 << b)) == 0 ? d[b] : -d[b];
            if (Math.Abs(sum) >= observed) extreme++;
        }
        return new Tail(extreme, total);
    }
}
```


`LessonLab/Experiment.cs`:
```csharp
using System.Globalization;

public static class Experiment
{
    public static Pair[] Cohort(int effect = -4, bool poor = false)
    {
        int[] baseline = [10, 14, 20, 28, 40, 52, 60, 76, 80, 100, 120, 144];
        Unit[] units = baseline.Select((y, i) => new Unit($"u{i}", y, y + effect)).ToArray();
        return Enumerable.Range(0, 6).Select(b => poor
            ? new Pair(units[b], units[b + 6])
            : new Pair(units[2 * b], units[2 * b + 1])).ToArray();
    }

    public static void Demo()
    {
        var pairs = Cohort();
        var seen = Design.Observe(pairs, 21);
        Console.WriteLine("pair,left_treated,left_seen,right_seen,treatment_minus_control");
        var d = Design.Differences(seen);
        for (int b = 0; b < seen.Length; b++)
            Console.WriteLine($"{b},{seen[b].LeftTreated},{seen[b].LeftOutcome},{seen[b].RightOutcome},{d[b]}");
        var p = Design.SharpNull(seen);
        Console.WriteLine($"estimate={Design.Estimate(seen):F4}; synthetic_oracle={Design.Oracle(pairs):F4}; sharp_null={p.Extreme}/{p.Total}={p.P:F4}");
    }

    public static void Run()
    {
        Console.WriteLine("effect,pairing,policy,estimate,design_mean,design_sd,min,max,sharp_null_p");
        using var csv = new StreamWriter("assignments.csv");
        csv.WriteLine("effect,pairing,mask,estimate");
        foreach (int effect in new[] { 0, -4 })
        foreach (bool poor in new[] { false, true })
        {
            var pairs = Cohort(effect, poor);
            double[] values = Design.Distribution(pairs);
            double mean = values.Average();
            double sd = Math.Sqrt(values.Average(x => (x - mean) * (x - mean)));
            string pairing = poor ? "poor" : "close";
            for (int mask = 0; mask < values.Length; mask++)
                csv.WriteLine(FormattableString.Invariant($"{effect},{pairing},{mask},{values[mask]:F8}"));
            var seen = Design.Observe(pairs, 21);
            Console.WriteLine($"{effect},{pairing},random-pair,{Design.Estimate(seen):F4},{mean:F4},{sd:F4},{values.Min():F4},{values.Max():F4},{Design.SharpNull(seen).P:F4}");
            var selected = Design.Observe(pairs, 63);
            // The randomization distribution is invalid for this deterministic policy.
            Console.WriteLine($"{effect},{pairing},select-low,{Design.Estimate(selected):F4},NA,NA,NA,NA,NA");
        }
        Console.WriteLine("# 64 equally weighted assignments per random-pair case; wrote assignments.csv; synthetic milliseconds, not measured latency");
    }
}
```


`LessonLab/Checks.cs`:
```csharp
public static class Checks
{
    private static void Require(bool ok, string message)
    {
        if (!ok) throw new Exception(message);
    }

    private static void Invalid(Action action)
    {
        try { action(); }
        catch (ArgumentException) { return; }
        throw new Exception("Invalid input accepted.");
    }

    private static int Bits(int mask)
    {
        int n = 0;
        while (mask != 0) { n += mask & 1; mask >>= 1; }
        return n;
    }

    public static void Run()
    {
        var pairs = Experiment.Cohort();
        double[] actual = Design.Distribution(pairs);
        // Independent oracle: select 6 of 12, retain one per pair, scan arm totals.
        var independent = new List<double>();
        for (int mask = 0; mask < (1 << 12); mask++)
        {
            if (Bits(mask) != 6) continue;
            long treatment = 0, control = 0;
            bool valid = true;
            for (int b = 0; b < 6; b++)
            {
                bool left = (mask & (1 << (2 * b))) != 0;
                bool right = (mask & (1 << (2 * b + 1))) != 0;
                if (left == right) { valid = false; break; }
                var p = pairs[b];
                treatment += left ? p.Left.Y1 : p.Right.Y1;
                control += left ? p.Right.Y0 : p.Left.Y0;
            }
            if (valid) independent.Add((double)(treatment - control) / 6);
        }
        Require(independent.Count == 64, "Assignment space differs.");
        Require(actual.Order().SequenceEqual(independent.Order()), "Independent arm scan differs.");
        Require(Math.Abs(actual.Average() - Design.Oracle(pairs)) < 1e-12, "Expectation differs.");
        Require(Math.Abs(actual.Average(x => (x + 4) * (x + 4)) - 1456.0 / 36) < 1e-12,
            "Design variance differs.");
        var seen = Design.Observe(pairs, 21);
        Require(Design.Differences(seen).SequenceEqual(new long[] { -8, 4, -16, 12, -24, 20 }),
            "Trace differs.");
        Require(Design.Estimate(seen) == -2, "Estimate differs.");

        // Exhaust all 3^8 potential-outcome tables for four units in two pairs.
        for (int table = 0; table < 6561; table++)
        {
            int code = table;
            var units = new Unit[4];
            for (int i = 0; i < 4; i++)
            {
                int y0 = code % 3; code /= 3;
                int y1 = code % 3; code /= 3;
                units[i] = new Unit($"id{i}", y0, y1);
            }
            Pair[] tiny = [new(units[0], units[1]), new(units[2], units[3])];
            long sum = 0;
            for (int mask = 0; mask < 4; mask++) sum += Design.Differences(Design.Observe(tiny, mask)).Sum();
            long effects = units.Sum(u => (long)u.Y1 - u.Y0);
            Require(sum == 2 * effects, "Unbiasedness identity differs.");
        }
        var nullPairs = Experiment.Cohort(0);
        int rejections = 0;
        for (int mask = 0; mask < 64; mask++)
        {
            var tail = Design.SharpNull(Design.Observe(nullPairs, mask));
            Require(tail.Total == 64 && tail.Extreme is >= 1 and <= 64, "Tail bounds differ.");
            if (20 * tail.Extreme <= tail.Total) rejections++;
        }
        Require(rejections == 2, "Sharp-null size differs.");
        Require(Design.SharpNull(Design.Observe(nullPairs, 63)).Extreme == 2, "Inclusive tails differ.");
        var equal = new[] { new Pair(new Unit("a", 5, 5), new Unit("b", 5, 5)) };
        Require(Design.SharpNull(Design.Observe(equal, 0)).P == 1, "Zero differences differ.");
        var reversed = seen.Select(s => new Seen(s.RightId, s.LeftId, !s.LeftTreated,
            s.RightOutcome, s.LeftOutcome)).ToArray();
        Require(Design.Estimate(reversed) == Design.Estimate(seen), "Pair relabeling differs.");
        Invalid(() => Design.Observe(pairs, -1));
        Invalid(() => Design.Observe(pairs, 64));
        Invalid(() => Design.Validate([]));
        Invalid(() => Design.Validate([new Pair(pairs[0].Left, pairs[0].Left)]));
        Invalid(() => Design.Validate([new Pair(new Unit("x", -1, 2), new Unit("y", 1, 2))]));
        Invalid(() => Design.Validate(Enumerable.Repeat(equal[0], 11).ToArray()));
        Invalid(() => Design.Estimate([]));
        Invalid(() => Design.Estimate([new Seen("a", "a", true, 1, 2)]));
        Console.WriteLine("PASS: 64 independent assignments; 6561 potential tables; variance; sharp-null size 2/64; ties; validation.");
    }
}
```


`LessonLab/Program.cs`:
```csharp
using System.Globalization;

CultureInfo.CurrentCulture = CultureInfo.InvariantCulture;
if (args.Length == 0) Experiment.Demo();
else if (args.SequenceEqual(new[] { "--check" })) Checks.Run();
else if (args.SequenceEqual(new[] { "--experiment" })) Experiment.Run();
else throw new ArgumentException("Use no arguments, --check or --experiment.");
```

Observed demo, also the expected replay output:
```text
pair,left_treated,left_seen,right_seen,treatment_minus_control
0,True,6,14,-8
1,False,20,24,4
2,True,36,52,-16
3,False,60,72,12
4,True,76,100,-24
5,False,120,140,20
estimate=-2.0000; synthetic_oracle=-4.0000; sharp_null=54/64=0.8438
```

Observed check output:
```text
PASS: 64 independent assignments; 6561 potential tables; variance; sharp-null size 2/64; ties; validation.
```

The independent scan selects 6 of 12 units with a 12-bit mask, keeps exactly one treatment per pair and scans arm totals directly; it does not call `Observe`/`Differences`. There are 924 balanced subsets, of which 64 obey the paired design. Comparing the full multisets preserves repeated estimates. The 6561 tables `3^8` exhaust potential outcomes 0,1,2 for four units in two pairs; an integer-sum identity checks unbiasedness without double approximation. Variance is checked against 1456/36; relabeling, ties, validation and null-size checks cover other mechanisms.

The 1-10 pair limit bounds enumeration at 1024 assignments. Outcomes are 0-10000 and IDs are nonempty/unique. Integer `long` sums and absolute-tail comparisons avoid orientation mistakes and floating-point p-value boundaries; printed means/SDs use rounded doubles. `Distribution` takes O(B*2^B) time and O(2^B+B) memory; `SharpNull` takes O(B*2^B) time and O(B) memory. This is bounded enumeration, not a large-scale statistical engine.

Checks cover the fixed table, the stated exhaustive small tables and selected edge cases; they do not prove every input, design or production model. The foundation proof supplies the general expectation argument under its assumptions. If execution is unavailable, check the six demo rows by hand, inspect the independent oracle, find the sign repair and interpret the next section's CSV. For a missing SDK, install the exact version or use the reading route; for a lock error, keep the supplied lock file. Changing dependencies/pins creates a different experiment. The ZIP's LICENSE/README supplement the complete runnable code here.

</details>


### A sharp-null test from observed outcomes

If every unit would have exactly the same outcome under either action, swapping the action labels leaves its observed outcome fixed. This **sharp null** states `Y_i(1)=Y_i(0)` for every unit. It is stronger than zero average effect, which allows positive and negative individual effects to cancel. Under the specified independent fair-pair assignment and sharp null, all `2^B` within-pair label flips are equally likely.

Use the observed pair differences as fixed values. For each sign-flip pattern, sum them with changed signs. Count patterns whose absolute sum is at least the observed absolute sum, including ties. Divide by `2^B` for the two-sided p-value. Division by B is common to all patterns, so compare integer sums directly. There is no Monte Carlo approximation or extra +1 correction because all allocations, including the observed one, are enumerated.

For one pair with observed outcomes 6 and 14, the null distribution of the contrast is {-8,+8}; both are as extreme as -8, so p=1. For six pairs the resolution is multiples of 1/64. Explain why the demo's p=54/64 does not show that treatment is ineffective or give a probability that the null is true.

<details>
<summary>Answer</summary>

The test counts how often the specified null assignment distribution produces an absolute contrast at least as large as observed. In this trace, 54 of 64 flips qualify. It is a tail probability under the sharp null and assignment assumptions, not `P(null | data)`. Failure to reject does not establish no effect: the simulator has effect -4 and only six pairs with wide assignment variation. Zero average effect is not the same sharp null. The model SD 6.3596 uses true potential outcomes across alternative assignments; the p-value freezes observed outcomes under a hypothetical no-effect model. They answer different questions.

</details>


The test needs the actual assignment probabilities, no interference and complete observed outcomes under the planned rule. With outcome-dependent allocation, missing outcomes or repeated looks, these flips do not justify the same reference distribution. A p-value is also not an interval for tau or the SD across possible true-effect assignments. We do not construct such an interval today.

Repair this defect in a separate lab copy: always compute `LeftOutcome - RightOutcome`, ignoring which side received treatment. Explain the earliest check that should fail and the correct repair. Re-run `--check` after the repair.

<details>
<summary>Answer</summary>

The independent arm-scan comparison runs before the trace check and detects the changed distribution. Right-treated pairs require right minus left, so the repair restores the conditional in `Differences`. The trace then yields [-8,4,-16,12,-24,20], rather than left-minus-right for every pair. Reversing left/right names while preserving assignment/outcomes must leave the estimate unchanged; that relabeling check also protects the meaning. The defect is not fixed by an absolute value, which would discard whether treatment improves or worsens the metric.

</details>


Pause - 10 minutes away from the screen.

## 6. Change one design choice at a time

**Controlled experiment · 45 minutes.** Record predictions, run the complete allocation enumeration and interpret the CSV. **Done when:** you can distinguish policy bias, design spread and a single example contrast without calling synthetic values production timings.

### Protocol before seeing results

**Assumptions:** twelve fixed units, no interference, complete outcomes, exactly two actions and the listed potential outcomes. The random-pair mathematical design gives each of the 64 assignments probability 1/64. The code enumerates this design; mask 21 is a fixed illustration, not a randomized production assignment.

**Controls:** retain the same twelve IDs and potential outcomes within each comparison. First compare random assignment against always selecting the lower-baseline unit under the close pairing. Next change only pairing: close pairs use adjacent sorted baselines; poor pairs match the first six with the last six. Keep the one-treated/one-control rule. Run each under a zero-effect table and under the constant -4 effect table as separate model scenarios.

**Predictions:** always selecting the lighter unit creates a negative contrast even with no effect. Random-pair means equal the oracle in both pairings. Close matching reduces the assignment SD for these fixed potential outcomes. One example contrast can have the wrong sign. Good matching is not a universal guarantee when outcomes/effects differ.

Run `dotnet run --no-restore -c Release --project LessonLab -- --experiment` from `dotnet`. Explain which rows isolate policy, which isolate pairing, and what `NA` means. Check `assignments.csv` has 256 data rows, four groups with 64 masks each and each group's equal-weight mean matching the oracle.

<details>
<summary>Answer - experiment results and limits</summary>

**Observed execution:** this output comes from the program above. `estimate` uses mask 21 for random-pair and mask 63 for select-low. `design_mean`, `design_sd`, `min`, `max` are equally weighted summaries of all 64 assignments, not wall-clock measurements or confidence intervals. `sharp_null_p` freezes mask 21's observed outcomes under the sharp null, not the true potential-outcome table.

```text
effect,pairing,policy,estimate,design_mean,design_sd,min,max,sharp_null_p
0,close,random-pair,2.0000,0.0000,6.3596,-14.0000,14.0000,0.8438
0,close,select-low,-14.0000,NA,NA,NA,NA,NA
0,poor,random-pair,6.0000,0.0000,28.8637,-69.3333,69.3333,0.8125
0,poor,select-low,-69.3333,NA,NA,NA,NA,NA
-4,close,random-pair,-2.0000,-4.0000,6.3596,-18.0000,10.0000,0.8438
-4,close,select-low,-18.0000,NA,NA,NA,NA,NA
-4,poor,random-pair,2.0000,-4.0000,28.8637,-73.3333,65.3333,0.9062
-4,poor,select-low,-73.3333,NA,NA,NA,NA,NA
# 64 equally weighted assignments per random-pair case; wrote assignments.csv; synthetic milliseconds, not measured latency
```

[Reproducible CSV](../../labs/experimental-design/assignments.csv). Experiment mode also creates this file locally. Each `(effect,pairing)` group contains masks 0-63; estimate is treatment minus control in synthetic milliseconds. Average all 64 estimates for the mean and take the square root of their mean squared deviation for SD. Do not divide by 63: this is the entire design distribution, not a sample of 64 draws.

Compare close/random-pair with close/select-low to hold pairing/outcomes fixed and change policy; select-low reports `NA` because the equal-probability reference distribution/p-value is unsupported for that policy. Compare close/random-pair with poor/random-pair to hold units/effect fixed and change pairing. SD rises from 6.3596 to 28.8637 while the mean still equals the effect. At effect=-4, poor-pair mask 21 gives +2 despite the true negative effect. One example's sign does not establish the effect's sign. At effect=0, close/select-low's -14 is selection bias. Changing effect from 0 to -4 retains design and shifts its mean -4.

**Inference:** the correct design protects expectation; good pretreatment matching reduces variance for this table. Exact enumeration of these four groups supports that bounded statement, not a universal matching improvement or a 4 ms production benefit.

</details>


### Limits and an invalid analysis to reject

The source data are constructed, not measured request durations. Exact enumeration eliminates Monte Carlo error for these small designs; it does not eliminate model error. Only 12 units, two effect scenarios and two pairings are covered. No RNG quality, network effects, actual matching algorithm, repeated stopping, missing telemetry, production representativeness or shared-resource interference was tested. We have not run the GrowthBook SDK or SQL Server/dashboard integration.

Suppose someone applies `SharpNull` to the deterministic `select-low` null scenario and reports p=2/64 as proof that the new implementation works. What is wrong, and how does the lab test check type-I error under the actual random design?

<details>
<summary>Answer</summary>

The actual deterministic policy assigns probability 1 to the all-left-treated mask, not 1/64 to each mask. Under zero effect it always selects lower outcomes, so its -14 contrast is selection, not treatment. Applying a fair-pair reference distribution to it invents a randomization that never happened. `NA` is the correct report in the experiment for that unsupported p-value. For the genuine fair-pair null design, exhaust every mask, build each observed dataset and compute its inclusive-tail p; exactly two have p<=0.05. The rejection probability is 2/64=0.03125. That checks size only for the fixed fixture. It is not evidence that the deterministic policy is valid.

</details>


A type-I error rejects a true null. Its probability is evaluated over the actual assignment design under the null. Discreteness and ties can make the size smaller than nominal; an observed finite-design check does not prove universal size for every dataset or assignment scheme.

Pause - 10 minutes away from the screen.

## 7. Transfer from latency to a packing outcome

**Changed context · 35 minutes.** Specify the assignment unit, run the binary-outcome example and distinguish a fraction difference from milliseconds. **Done when:** you can target the eight fixed packing units and name what prevents extension to every warehouse.

A warehouse compares two packing procedures. Four pretreatment pairs contain eight assignment units; the four pair choices are independent, while assignments within a pair are complementary. Each outcome is 1 for damage and 0 for no damage during a fixed follow-up window. The simulator's potential outcomes are `(Y0,Y1)`: a=(0,0), b=(1,0), c=(1,0), d=(1,1), e=(0,0), f=(0,1), g=(1,0), h=(0,0). Pair (a,b),(c,d),(e,f),(g,h), then inspect mask 5. Define the effect target, calculate the observed difference and sharp-null p, and independently check the design mean. Use a separate lab copy, replace only `Program.cs`, and keep the other files.

<details>
<summary>Answer - packing context and complete program</summary>

The target is the average effect on the eight fixed units: total effect -2 divided by 8 is -0.25, a 25 percentage-point reduction in this synthetic cohort's damage rate if all units switch actions. Mask 5 gives pair differences [-1,0,0,-1] and D=-0.5, an observed 50 percentage-point reduction, not 0.5 ms. The two nonzero differences have four sign combinations; the two same-sign combinations reach absolute sum 2, giving p=8/16=0.5 including signs for the zero pairs.

Replace `Program.cs` with this complete code, restore/run using the same lab commands:
```csharp
using System.Globalization;
CultureInfo.CurrentCulture = CultureInfo.InvariantCulture;
Pair[] pairs = [
    new(new Unit("a", 0, 0), new Unit("b", 1, 0)),
    new(new Unit("c", 1, 0), new Unit("d", 1, 1)),
    new(new Unit("e", 0, 0), new Unit("f", 0, 1)),
    new(new Unit("g", 1, 0), new Unit("h", 0, 0))
];
var seen = Design.Observe(pairs, 5);
var tail = Design.SharpNull(seen);
// Independent expectation: directly sum all eight unit effects.
double direct = pairs.SelectMany(p => new[] { p.Left, p.Right })
    .Sum(u => (double)u.Y1 - u.Y0) / 8;
if (Design.Estimate(seen) != -0.5 || direct != -0.25 || tail.P != 0.5 ||
    Design.Distribution(pairs).Average() != direct)
    throw new Exception("Packing result differs.");
Console.WriteLine($"observed={Design.Estimate(seen):F4}; cohort_effect={direct:F4}; sharp_null={tail.Extreme}/{tail.Total}={tail.P:F4}");
```

Expected output verified by execution:

```text
observed=-0.5000; cohort_effect=-0.2500; sharp_null=8/16=0.5000
```

Directly summing unit effects independently checks the enumerated mean. One unit has effect +1, so individual effects vary; tau is nonzero here. Only the implemented individual sharp-null test is used, not a test of zero average effect. This model does not validate an actual packing procedure or every warehouse/date.

</details>


Now suppose each packing unit is a batch with ten packages. All ten outcomes in a batch are linked and the procedure is assigned by batch. Can you pretend to have 80 independent assignments, and what changes if one arm's damaged batches lose their records?

<details>
<summary>Answer</summary>

There are eight assigned batch units, not eighty independent allocations. Equal batch sizes and one well-defined batch summary can keep the target interpretable, but package-weighted effects with unequal sizes need an explicit estimand and weights. Missing outcomes linked to damage and arm can select the comparison even after proper randomization. Count assignments and missing outcomes by arm, investigate causes and apply the prespecified policy/sensitivity analysis. Silently dropping damaged batches is not a valid repair. Our complete-outcome test gives no guarantee for that missing-data mechanism.

</details>


## 8. Write a claim that survives its assumptions

**Synthesis · 45 minutes.** Write a short experiment proposal and a bounded result paragraph using the worked template. **Done when:** both distinguish target, assignment, observation, uncertainty and unverified scope. No submission is required; the answers remain available.

Write a 150-200 word proposal for a .NET service comparison: target cohort and unit, frozen versions, pretreatment pairing/eligibility, randomization probabilities, primary metric/window, stop rule, missing-data handling and interference check. Why can a hash-based 50/50 rollout need a different analysis from the lab's exactly one-per-pair allocation?

<details>
<summary>Answer</summary>

For a synthetic pilot, target the eligible tenants enrolled before launch, not all future traffic. Freeze control and treatment versions and a seven-day outcome window. Pair tenants using pretreatment volume bands and region before any treatment is delivered. Within each pair, independently assign either tenant to treatment with probability one half; log the experiment version and assignment once per tenant. Use mean tenant-level failed-request fraction as the primary metric and stop after the fixed window, without stopping for a favorable p-value. Count every assigned tenant, report missing telemetry by arm and investigate its cause; do not silently delete tenants with missing outcomes. If recovery is impossible, report the comparison as incomplete and provide a prespecified sensitivity analysis rather than an unqualified effect. Check whether tenants share capacity-limited resources and whether treatment can alter another tenant's outcome. Isolate resources or redesign the assignment if needed. Audit delivered versions, identities, exposure and outcome joins before reporting an assignment effect. The pilot's causal target is this enrolled cohort under these assumptions; extrapolating to other tenants or dates requires additional evidence.

A hash-based rollout can give zero, one or two treated tenants per chosen pair. Its assignment space/probabilities differ; our one-per-pair sign-flip test is not automatically valid. Even a nominal 50/50 setting does not guarantee exact realized counts.

</details>


Write a result paragraph for the constant -4 close-pair case. Separate assumptions, prediction, observation and inference. Include both the model SD and the sharp-null result with their different interpretations.

<details>
<summary>Answer</summary>

Assume the twelve fixed synthetic units, complete outcomes, no interference and independent fair assignment within the six close pairs. We predicted that the mean contrast over assignment would equal -4. Enumeration observed a design mean -4.0000, SD 6.3596 and range [-18,10]. The preselected mask 21 gives -2.0000, while the observed-outcome sharp-null test gives 54/64=0.84375. The estimator targets the cohort effect in expectation; one allocation does not recover it exactly. The SD describes known-potential-outcome assignment spread, not a production interval. The p-value provides no evidence against the sharp null at 0.05 in this example, but does not establish zero effect. These results concern four enumerated synthetic scenarios, not production latency, future cohorts, the GrowthBook statistical engine or SQL Server.

</details>


Finish with one next question whose answer would strengthen a real comparison. Explain a feasible first check and what it would still leave unresolved.

<details>
<summary>Answer</summary>

Ask whether treatment changes a shared queue seen by control tenants. First audit resource sharing and log queue load with assignment/version/time in a sandbox under a fixed workload. If both arms influence that queue, the independent-unit model is unsuitable; isolate resources or design cluster/time-block allocation before analyzing outcomes. That audit can identify interference mechanisms, but cannot establish all production traffic patterns, long-term stability or the validity of a replacement design without further checks. Do not promote the mock oracle's known tau into a claim about a deployed system.

</details>

<!-- LESSON_NAVIGATION_START -->
## Related reading

- [Lesson 07 - Sampling uncertainty: more records need not mean more evidence](../2026-10-11-sampling-uncertainty/lesson.md) - Reuse expectation, variance and the distinction between rows and independent units.
- [Lesson 05 - Indexes and query plans: when a seek still does much work](../2026-10-09-index-query-plans/lesson.md) - A correct query/order does not establish that comparison cohorts are comparable.
- [Lesson 01 - Big-O and data structures: removing duplicate order IDs in C#](../2026-10-05-cost-model/lesson.md) - Revisit the workload and model limits of a benchmark.
- [C# lab guide](../../labs/experimental-design/dotnet/README.md) - Pinned environment, assignment enumeration and inference limits.

---

[← Previous: Lesson 07 - Sampling uncertainty: more records need not mean more evidence](../2026-10-11-sampling-uncertainty/lesson.md) · [All lessons](../../README.md)
<!-- LESSON_NAVIGATION_END -->
