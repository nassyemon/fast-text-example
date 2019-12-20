import client from "./esclient";
import splitByTag from "./splitByTag"


export default async (terms, slop=50) => {
  const ret = await client.search({
      index: "docs",
      body: {
        query: {
            bool: {
                should: [
                    {
                        match_phrase: {
                            "text": {
                                query : terms.join(" "),
                                slop,
                            }
                        },
                    },
                    {
                        match_phrase: {
                            "text": {
                                query : [...terms].reverse().join(" "),
                                slop,
                            }
                        },
                    }
                ],
                minimum_should_match: 1,
            },
        },
        _source: ["name", "doc_id", "text"],
        highlight: {
            type: "fvh",
            boundary_chars: "*＊.,!? 。、\t\n・",
            boundary_scanner_locale: "ja-JP",
            boundary_scanner: "chars",
            number_of_fragments: 1,
            fragment_size: 300,
            fields: [{ "text": {} }],
        },
      },
    size: 10,
  });
  const { hits: { total: { value: totalValue } , hits } } = ret;
  console.log(hits);
  return {
      terms,
      total: totalValue,
      results: Array.isArray(hits) ? hits.map(parseDoc) : null,
  };
};

function parseDoc({ _source, highlight }) {
    const { text } = highlight;
    const higlighted = Array.isArray(text) && text.length > 0 ? text[0]: null;
    return {
        ..._source,
        highlight: higlighted ? splitByTag(higlighted) : null,
    }
}