import styled from "styled-components";

export const SearchResults = styled.div`
margin-top: 20px;
width: 80%;
position: relative;
`;

export const BaseSearchResult = styled.div`
 width: 100%;
 margin: 20px 0px;
 position: relative;
 display: flex;
 flex-direction: column;
 border: 3px solid #38ab6c;
`

export const BaseSearchHeader = styled.h3`
 padding-left: 10px;
 margin: 0px;
 font-weight: bolder;
 background: #38ab6c;
 color: #ffffff;
`;

export const BaseSearchList = styled.div`
 display:flex;
 flex-direction: column;
 flex-wrap: wrap;
`

export const BaseSearchItem = styled.span`
 margin: 5px 5px 0px 5px;
 padding: 3px;
 border: 1px solid #dddddd;
`;

export const Text = styled.div`
  display: div;
  font-size: 10px;
  overflow: hidden;
  width: 100%;
  height: 100%;
  text-align: left;
  max-height: 180px;
  box-sizing: border-box;
`;

export const SearchItemSpan = styled.span``;
export const SearchItemHighlight = styled.span`
  font-weight: bold;
  background-color: #f7f07a;
`;
