import searchDocs from "./searchDocs";

export default async (pre, post, alternatives) => {
  const searches = alternatives.reduce((acc, word) => {
    if (typeof word !== "string"){
      return word;
    }
    const terms = [...pre, word, ...post];
    return [...acc, Promise.all([terms, searchDocs(terms)])];
  }, []);
  const results = await Promise.all(searches);
  return results.filter(([terms, searched]) => searched.total > 0 && results.length > 0);
};
