import client from "./esclient";

export default async (baseWords, alternatives) => {
  console.log(baseWords, alternatives);
  const baseCond = {
    "bool": {
      "must": baseWords.map(word => ({ "term": { "wakati": word } })),
    }
  };
  const aggs = alternatives.reduce((acc, alt) => {
    if (typeof alt !== "string" || alt.match(/\s/)){
      return acc;
    }
    acc[alt] = {
      "filter" : { 
          "bool": {
            "must": [
              ...baseWords.map(word => ({ "term": { "wakati": word } })),
              { "term": { "wakati": alt } } 
            ]
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
