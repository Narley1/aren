function h2(x, y){
  let n = Math.imul(x|0, 374761393) + Math.imul(y|0, 668265263);
  n = Math.imul(n ^ (n >>> 13), 1274126177);
  return ((n ^ (n >>> 16)) >>> 0) / 4294967296;
}
function vnoise(x, y){
  const xi = Math.floor(x), yi = Math.floor(y), xf = x - xi, yf = y - yi;
  const s = t => t*t*(3-2*t), u = s(xf), v = s(yf);
  const a = h2(xi,yi), b = h2(xi+1,yi), c = h2(xi,yi+1), d = h2(xi+1,yi+1);
  return a + (b-a)*u + (c-a)*v + (a-b-c+d)*u*v;
}
