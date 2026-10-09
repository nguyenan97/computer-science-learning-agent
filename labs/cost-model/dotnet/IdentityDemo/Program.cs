using Microsoft.Data.Sqlite;
using Microsoft.EntityFrameworkCore;

using var connection = new SqliteConnection("Data Source=:memory:");
connection.Open();
var options = new DbContextOptionsBuilder<BlogDb>()
    .UseSqlite(connection).Options;
using (var seed = new BlogDb(options))
{
    seed.Database.EnsureCreated();
    var blog = new Blog { Id = 1 };
    seed.Posts.AddRange(
        new Post { Id = 1, Blog = blog },
        new Post { Id = 2, Blog = blog });
    seed.SaveChanges();
}

Check("Tracking", 0, expectedSame: true, expectedTracked: 3);
Check("NoTracking", 1, expectedSame: false, expectedTracked: 0);
Check("IdentityResolution", 2, expectedSame: true, expectedTracked: 0);
Console.WriteLine("All checks passed.");

void Check(string name, int mode, bool expectedSame, int expectedTracked)
{
    using var db = new BlogDb(options);
    IQueryable<Post> query = db.Posts.Include(p => p.Blog).OrderBy(p => p.Id);
    query = mode switch
    {
        1 => query.AsNoTracking(),
        2 => query.AsNoTrackingWithIdentityResolution(),
        _ => query
    };
    var posts = query.ToList();
    if (posts.Count != 2 || posts.Any(p => p.Blog.Id != 1))
        throw new InvalidOperationException("Expected two posts for Blog 1.");
    bool same = ReferenceEquals(posts[0].Blog, posts[1].Blog);
    int tracked = db.ChangeTracker.Entries().Count();
    Console.WriteLine($"{name}: sameBlog={same}, tracked={tracked}");
    if (same != expectedSame || tracked != expectedTracked)
        throw new InvalidOperationException($"Unexpected result for {name}.");
}

sealed class BlogDb(DbContextOptions<BlogDb> options) : DbContext(options)
{
    public DbSet<Post> Posts => Set<Post>();
}

sealed class Blog
{
    public int Id { get; set; }
}

sealed class Post
{
    public int Id { get; set; }
    public int BlogId { get; set; }
    public Blog Blog { get; set; } = null!;
}
