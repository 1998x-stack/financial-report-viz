(() => {
"use strict";
const search=document.getElementById("concept-search");
const buttons=Array.from(document.querySelectorAll("[data-glossary-filter]"));
const cards=Array.from(document.querySelectorAll("[data-glossary-card]"));
const sections=Array.from(document.querySelectorAll("[data-glossary-section]"));
const count=document.querySelector(".glossary-search-count");
const empty=document.querySelector(".glossary-empty");
if(!cards.length || !search)return;
let category="all";
function apply(){
  const term=search.value.trim().toLocaleLowerCase();
  let shown=0;
  for(const card of cards){
    const match=(category==="all"||card.dataset.category===category)
                && card.dataset.search.toLocaleLowerCase().includes(term);
    card.hidden=!match;
    shown+=Number(match);
  }
  for(const section of sections){
    section.hidden=!Array.from(section.querySelectorAll("[data-glossary-card]")).some(x=>!x.hidden);
  }
  if(count)count.textContent="显示 "+shown+" / "+cards.length+" 个概念";
  if(empty)empty.hidden=shown>0;
}
search.addEventListener("input",apply);
search.addEventListener("keydown",e=>{if(e.key==="Escape"){search.value="";apply();}});
for(const button of buttons){
  button.addEventListener("click",()=>{
    category=button.dataset.glossaryFilter;
    for(const b of buttons){
      const active=b===button;
      b.setAttribute("aria-pressed",String(active));
      b.classList.toggle("selected",active);
    }
    apply();
  });
}
apply();
})();