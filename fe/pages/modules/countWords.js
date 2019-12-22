import client from "./esclient";

export default async (terms) => {
  // console.error(terms);
  const aggs = terms.reduce((acc, word) => {
    if (typeof word !== "string" || word.match(/\s/)){
      return acc;
    }
    acc[word] = { 
      "filter" : { 
          "term": {
            "wakati" : word,
          }
       }
    };
    return acc;
  }, {});

  const ret = await client.search({
    index: "docs",
    body: {
      aggs,
    },
    size: 0,
  });
  const { aggregations } = ret;
  return Object.entries(aggregations).reduce((acc, [key, { doc_count }]) => ({
    ...acc,
    [key]: doc_count
  }), {});
};
