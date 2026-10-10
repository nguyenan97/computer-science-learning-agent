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
