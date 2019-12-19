import qs from "query-string";

const baseUrl = "http://localhost:5000/related/search"
export default async (terms) => {
  const params = qs.stringify({ q: terms.join(" ") })
  const url = `${baseUrl}?${params}`
  const ret = await fetch(url);
  console.log(ret);
  const response = await ret.json()
  console.log(response);
  if (!response || !Array.isArray(response.results)) {
    return null;
  }
  const { results } = response;
  if(results.length < 0) {
      return null;
  }
  return results.map(({ word }) => ({ word }));
}