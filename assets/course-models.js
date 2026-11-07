/* Small, deterministic rules shared by browser demonstrations and verification. */
(function(root){
  const models={
    affordable(items,budget,minutes=Infinity){return items.filter(item=>item.price<=budget&&item.minutes<=minutes).map(item=>item.name);},
    remaining(budget,price){return budget-price;},
    vending(coins,price=150){let paid=0,lines=[];for(const coin of coins){if(paid>=price)break;paid+=coin;lines.push('Paid: '+paid);}lines.push(paid>=price?'Change: '+(paid-price):'Due: '+(price-paid));return {paid,lines};},
    largeBoxes(boxes,minimum){return boxes.filter(b=>b.w*b.h>=minimum);},
    hit(score,seconds){return seconds>0?score+1:score;},
    tick(seconds){return Math.max(0,seconds-1);},
    inside(x,y,left,top,width,height){return left<=x&&x<=left+width&&top<=y&&y<=top+height;}
  };
  if(typeof module!=='undefined'&&module.exports)module.exports=models;
  else root.CourseModels=models;
})(typeof globalThis==='undefined'?this:globalThis);
