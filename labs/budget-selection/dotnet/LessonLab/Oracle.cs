// Exhaustive independent reference for small instances, original MIT code.
public static class Oracle
{
    public static Choice Solve(Job[] jobs, int capacity)
    {
        Budget.Validate(jobs, capacity);
        if (jobs.Length > 22) throw new ArgumentOutOfRangeException(nameof(jobs), "Oracle limit is 22 jobs.");
        long best = 0, work = 0;
        int bestMask = 0, bestCost = 0;
        for (int mask = 0; mask < (1 << jobs.Length); mask++)
        {
            work++;
            long cost = 0, value = 0;
            for (int i = 0; i < jobs.Length; i++)
                if ((mask & (1 << i)) != 0)
                {
                    cost += jobs[i].Cost;
                    value = checked(value + jobs[i].Value);
                }
            if (cost <= capacity && value > best)
            {
                best = value;
                bestCost = (int)cost;
                bestMask = mask;
            }
        }
        int[] indices = Enumerable.Range(0, jobs.Length).Where(i => (bestMask & (1 << i)) != 0).ToArray();
        return new Choice(best, bestCost, indices, work);
    }
}
