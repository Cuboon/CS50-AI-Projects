import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    T = len(corpus)

    # Initialize distribution with all pages
    distribution = {
        p: (1 - damping_factor) / T
        for p in corpus
    }

    # If page has outgoing links
    if corpus[page]:
        for linked_page in corpus[page]:
            distribution[linked_page] += damping_factor / len(corpus[page])

    # If page has NO outgoing links → treat as linking to all pages
    else:
        for p in corpus:
            distribution[p] = 1 / T

    return distribution


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    PageRank = {}

    # keeps track of the nujmber of visits in each page
    PageVisits = {page: 0 for page in corpus}

    # first page
    page = random.choice(list(corpus.keys()))

    for _ in range(n):

        # update page visits
        PageVisits[page] += 1

        # update the given page via the transition_model function
        model = transition_model(corpus, page, damping_factor)

        page = random.choices(list(model.keys()), weights=model.values())[0]

    # calculating the pagerank
    for p in PageVisits:
        PageRank[p] = PageVisits[p] / n

    return PageRank


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    # distribute probability
    PageRank = {page: 1 / len(corpus) for page in corpus}

    # convergence margin
    margin = 0.001

    # loop until values converge
    while True:

        new_rank = {}

        # distribute random probability
        for page in corpus:
            new_rank[page] = (1 - damping_factor) / len(corpus)

        # distribute and add the probabilities of the linked pages
        for page in corpus:
            # check if links are present on the curent page
            if corpus[page]:
                for p in corpus[page]:
                    new_rank[p] += damping_factor * (PageRank[page] / len(corpus[page]))

            # if there are no links on the page
            else:
                for p in corpus:
                    new_rank[p] += damping_factor * (PageRank[page] / len(corpus))

        # check margin
        if max(abs(new_rank[p] - PageRank[p]) for p in PageRank) < margin:
            break

        PageRank = new_rank

    return PageRank


if __name__ == "__main__":
    main()
