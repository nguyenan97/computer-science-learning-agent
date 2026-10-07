// Small deterministic generator for reproducible teaching, not for security.
public sealed class Draws
{
    private const long Modulus = 2147483647;
    private long state;
    public Draws(int seed)
    {
        if (seed < 1 || seed >= Modulus) throw new ArgumentOutOfRangeException(nameof(seed));
        state = seed;
    }
    public int NextRaw() { state = 48271 * state % Modulus; return (int)state; }
    public int Below(int bound)
    {
        if (bound < 1 || bound > 10000) throw new ArgumentOutOfRangeException(nameof(bound));
        long limit = (Modulus - 1) - (Modulus - 1) % bound;
        long value;
        do { value = NextRaw() - 1L; } while (value >= limit);
        return (int)(value % bound);
    }
    public int Bernoulli(int a, int b)
    {
        if (b < 1 || b > 10000 || a < 0 || a > b) throw new ArgumentOutOfRangeException(nameof(a));
        return Below(b) < a ? 1 : 0;
    }
}
