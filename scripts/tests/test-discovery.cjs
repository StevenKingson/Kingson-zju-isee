const assert = require('node:assert/strict');
const {safePath, cleanEntries, filterCourses} = require('../../docs/javascripts/discovery.js');
const root = new URL('https://example.com/Kingson-zju-isee/');
assert.equal(safePath('course/year1/', root), 'course/year1/');
assert.equal(safePath('https://example.com/Kingson-zju-isee/acg/diary/?test=1#review', root), 'acg/diary/');
for (const url of ['javascript:alert(1)', '//evil.example/', '/other-site/', '../private/', 'https://user:pass@example.com/Kingson-zju-isee/course/', null]) {
  assert.equal(safePath(url, root), null, `Unsafe stored URL: ${url}`);
}
assert.deepEqual(cleanEntries(null, root), []);
const cleaned = cleanEntries([{title:'  课程  ',url:'course/',time:2},
  {title:'duplicate',url:'course/',time:1}, {title:'external',url:'https://evil.example/'},
  {title:'',url:'about/'}, {url:'friends/'}, {title:'about',url:'about/',time:3}],root,1);
assert.deepEqual(cleaned,[{title:'课程',url:'course/',time:2}]);
const courses = [
  {title:'电子工程训练（甲）',aliases:'电工训',category:'专业必修课程',year:'大一',url:'course/a/',reports:'course/a/reports/',downloads:6},
  {title:'电子电路设计实验Ⅱ',aliases:'电设2',category:'实验课',year:'大二',url:'course/b/',reports:'course/b/reports/',downloads:2},
  {title:'微观经济学（甲）',aliases:'味精',category:'个性修读课程',year:'大二',url:'course/c/',reports:null,downloads:0}
];
const base = {q:'',year:'',category:'',type:''};
assert.equal(filterCourses(courses,{...base,q:'电工训'})[0].year,'大一');
assert.equal(filterCourses(courses,{...base,q:'电设 ２'})[0].url,'course/b/');
assert.equal(filterCourses(courses,{...base,year:'大二',type:'reports'}).length,1);
assert.equal(filterCourses(courses,{...base,category:'个性修读课程',type:'downloads'}).length,0);
assert.equal(filterCourses(courses,{...base,type:'saved'},new Set(['course/c/']))[0].aliases,'味精');
assert.equal(filterCourses(courses,{...base,q:'no such course'}).length,0);
console.log('Passed: bookmark URL validation, corrupt storage, deduplication, aliases and combined course filters.');
