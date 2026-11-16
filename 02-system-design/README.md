# 02 · System design

[Home](../README.md) · [CS fundamentals](../05-cs-fundamentals/README.md) · [Mock interviews](../06-mock-interviews/README.md) · [Spaced repetition](../07-study-plan/spaced-repetition.md)

New-grad loops mostly ask **object-oriented design** and **light system design**, so this section covers both:

- **[concepts/](concepts/README.md)**: building blocks (caching, sharding, queues, rate limiting, ...). Each note ends in flashcards and is reviewed as one item.
- **[questions/](questions/README.md)**: one folder per classic question (`url-shortener/design.md`), timed as a 45-minute mock with per-phase times.
- **[ood/](ood/README.md)**: class-level designs (parking lot, LRU cache, rate limiter class).

**45-minute mock, by phase:** requirements 5 · estimates 5 · API/data model 10 · high-level design 15 · deep dive 10. Run `prep start sd <name>`, type `prep phase` at each boundary, then `prep stop`.

**Reviews** mean redrawing the design from memory with the note closed, then comparing.

## Index

<!-- prep:index:start -->
| Section | Entries | Due now |
|---|---:|---:|
| [Concepts](concepts/README.md) | 1 | 1 |
| [Design questions](questions/README.md) | 1 | 1 |
| [Object-oriented design](ood/README.md) | 0 | 0 |

**Phase timing** (avg of 2 timed designs)

| Phase | Target | Avg | Delta |
|---|---:|---:|---:|
| requirements | 5m | 5.5m | +0.5m |
| estimates | 5m | 6.0m | +1.0m |
| api-data-model | 10m | 10m | +0.0m |
| high-level-design | 15m | 17m | +2.0m |
| deep-dive | 10m | 9.5m | -0.5m |
<!-- prep:index:end -->

## Reading list

- [donnemartin/system-design-primer](https://github.com/donnemartin/system-design-primer)
- [ByteByteGo blog](https://blog.bytebytego.com/)
- *Designing Data-Intensive Applications* (Kleppmann): chapters 1 to 9
