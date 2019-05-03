# Note

We use the "standard" analyzer because it is the "best general choice for
analyzing text"(https://www.elastic.co/guide/en/elasticsearch/guide/current/analysis-intro.html),
but this is just future-proofing. Moreover, the completion suggester only
prefix-matches, so the analyzer doesn't tokenize and generate inputs for us.
