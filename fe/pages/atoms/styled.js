import styled from "styled-components";

export const Search = styled.div`
 width: 50%;
 position: relative;
 display: flex;
`;

export const SearchTerm = styled.input.attrs({
   type: "text"
})`
 width: 100%;
 border: 3px solid #00B4CC;
 border-right: none;
 padding: 5px;
 height: 20px;
 border-radius: 5px 0 0 5px;
 outline: none;
 color: #555555;
 &:focus {
   font-weight: bold;
   color: #000000;
 },
`;

export const SearchButton = styled.button.attrs({ 
   type: "submit"
})`
 width: 80px;
 height: 36px;
 border: 1px solid #00B4CC;
 background: #00B4CC;
 text-align: center;
 color: #fff;
 border-radius: 0 5px 5px 0;
 cursor: pointer;
 font-size: 20px;
`;

export const Wrap = styled.div`
 width: 100%;
 top: 10%;
 left: 10%;
 position: absolute;
`;

export const WordResults = styled.div`
 width: 80%;
 position: relative;
`;

export const SyononymResult = styled.div`
 width: 100%;
 margin: 20px 0px;
 position: relative;
 display: flex;
 flex-direction: column;
 border: 3px solid #00B4CC;
`

export const SyononymHeader = styled.h3`
 padding-left: 10px;
 margin: 0px;
 font-weight: bolder;
 background: #00B4CC;
 color: #ffffff;
`;

export const SyonoymList = styled.div`
 display:flex;
 flex-direction: row;
 flex-wrap: wrap;
`

export const Syononym = styled.div`
 margin: 0px 5px;
 display: flex;
 color: ${props => props.count ? "#000000": "#888888"};
`;

export const WordCount = styled.span`
  font-size: 10px;
  color: ${props => props.count ? "#dd3300": "#aaaaaa"};
  font-weight: ${props => props.count ? "bolder": ""};
  align-self: center;
`;

export const RelatedWordResult = styled(SyononymResult)`
 border-color: #cc317c;
`

export const RelatedWordHeader = styled(SyononymHeader)`
 background: #cc317c;
`;