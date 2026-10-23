import json
S="https://vega.github.io/schema/vega-lite/v5.json"
G="data/six_year_by_group.csv"; I="data/institution_six_year.csv"
BLUE,LB,GREY="#1f5fa8","#9ecae1","#9aa5b1"
cfg={"font":"Helvetica, Arial, sans-serif","view":{"stroke":None},"axis":{"labelFontSize":12,"titleFontSize":12,"grid":False}}
def base(h=260): return {"$schema":S,"width":"container","height":h,"config":cfg}
def save(n,s): json.dump(s,open(f"specs/{n}.json","w"),indent=2)
xpct={"field":"completed","type":"quantitative","title":"Completed within 6 years (%)","scale":{"domain":[0,100],"zero":True}}
def lolli(filt,sort,h):
    s=base(h); s["data"]={"url":G}; s["transform"]=[{"filter":filt}]
    s["encoding"]={"y":{"field":"group","type":"nominal","sort":sort,"title":None}}
    s["layer"]=[{"mark":{"type":"rule","color":GREY},"encoding":{"x":xpct,"x2":{"datum":0}}},
                {"mark":{"type":"circle","size":90,"color":BLUE},"encoding":{"x":xpct,"tooltip":[{"field":"group"},{"field":"completed","title":"%"}]}}]
    return s
save("s01_trend",{**base(240),"data":{"url":G},"transform":[{"filter":"datum.section=='National' && indexof(datum.group,'National Total')>=0"}],
 "mark":{"type":"line","point":True,"color":BLUE},"encoding":{"x":{"field":"cohort_start","type":"quantitative","title":"Year students started","axis":{"format":"d","tickMinStep":2}},
 "y":{"field":"completed","type":"quantitative","title":"Completed within 6 years (%)","scale":{"domain":[0,100],"zero":True}}}})
save("s02_field_lollipop",lolli("datum.section=='Broad Field of Education(d)' && datum.cohort_start==2017",{"field":"completed","op":"max","order":"descending"},300))
d=base(300); d["data"]={"url":G}
d["transform"]=[{"filter":"datum.section=='Broad Field of Education(d)' && (datum.cohort_start==2005 || datum.cohort_start==2017)"},
 {"pivot":"cohort_start","value":"completed","groupby":["group"]},{"filter":"isValid(datum['2005']) && isValid(datum['2017'])"}]
col=lambda n:{"datum":n,"type":"nominal","scale":{"domain":["2005 cohort","2017 cohort"],"range":[GREY,BLUE]},"legend":{"title":None,"orient":"top"}}
xs={"type":"quantitative","title":"Completed within 6 years (%)","scale":{"domain":[0,100],"zero":True}}
d["encoding"]={"y":{"field":"group","type":"nominal","title":None,"sort":{"field":"2017","op":"max","order":"descending"}}}
d["layer"]=[{"mark":{"type":"rule","color":GREY},"encoding":{"x":{"field":"2005",**xs},"x2":{"field":"2017"}}},
 {"mark":{"type":"circle","size":90,"opacity":1},"encoding":{"x":{"field":"2005",**xs},"color":col("2005 cohort")}},
 {"mark":{"type":"circle","size":90,"opacity":1},"encoding":{"x":{"field":"2017",**xs},"color":col("2017 cohort")}}]
save("s03_field_dumbbell",d)
geo={"url":"data/australia_states.geojson","format":{"type":"json","property":"features"}}
proj={"type":"equalEarth"}
c={**base(360),"data":geo,"projection":proj,"transform":[{"lookup":"properties.STATE_NAME","from":{"data":{"url":"data/abs_attainment_by_state.csv"},"key":"state","fields":["bachelor_pct"]}}],
 "mark":{"type":"geoshape","stroke":"white","strokeWidth":0.7},
 "encoding":{"color":{"field":"bachelor_pct","type":"quantitative","title":"% with a bachelor degree","scale":{"scheme":"blues","domain":[10,30]}},
 "tooltip":[{"field":"properties.STATE_NAME","title":"State"},{"field":"bachelor_pct","title":"% bachelor degree"}]}}
save("s04_choropleth",c)
m={**base(360),"projection":proj,"layer":[
 {"data":geo,"mark":{"type":"geoshape","fill":"#e7ebef","stroke":"white"}},
 {"data":{"url":I},"transform":[{"filter":"datum.cohort_start==2017"},{"lookup":"institution","from":{"data":{"url":"data/university_locations.csv"},"key":"institution","fields":["lat","lon"]}},{"filter":"isValid(datum.lat)"}],
  "mark":{"type":"circle","size":90,"stroke":"white","opacity":0.95},
  "encoding":{"longitude":{"field":"lon","type":"quantitative"},"latitude":{"field":"lat","type":"quantitative"},
  "color":{"field":"completion_rate","type":"quantitative","title":"Completed in 6 years (%)","scale":{"scheme":"viridis","domain":[30,90]}},
  "tooltip":[{"field":"institution"},{"field":"completion_rate","title":"% completed"}]}}]}
save("s05_symbol_map",m)
t={**base(260),"width":240,"data":{"url":I},"transform":[{"filter":"datum.cohort_start==2017 && datum.state!='Multi-State'"},
 {"aggregate":[{"op":"mean","field":"completion_rate","as":"completed"}],"groupby":["state"]},
 {"lookup":"state","from":{"data":{"url":"data/tiles.csv"},"key":"state","fields":["abbr","col","row"]}}],
 "encoding":{"x":{"field":"col","type":"ordinal","axis":None},"y":{"field":"row","type":"ordinal","axis":None}},
 "layer":[{"mark":{"type":"rect","stroke":"white","strokeWidth":3},"encoding":{"color":{"field":"completed","type":"quantitative","title":"Average completed (%)","scale":{"scheme":"blues","domain":[40,80]}},
  "tooltip":[{"field":"state"},{"field":"completed","title":"Average %","format":".1f"}]}},
  {"mark":{"type":"text","fontSize":13,"fontWeight":"bold"},"encoding":{"text":{"field":"abbr"},"color":{"condition":{"test":"datum.completed>62","value":"white"},"value":"#1a1a1a"}}}]}
save("s06_tile_grid",t)
r=base(200); r.pop("width"); r["data"]={"url":G}
r["transform"]=[{"filter":"datum.section=='Regional Classification ( c )'"}]
r["facet"]={"column":{"field":"group","type":"nominal","sort":["Metropolitan","Regional","Remote"],"title":None}}
r["spec"]={"width":170,"height":200,"mark":{"type":"line","point":True,"color":BLUE},"encoding":{"x":{"field":"cohort_start","type":"quantitative","title":"Year started","axis":{"format":"d","tickCount":3}},
 "y":{"field":"completed","type":"quantitative","title":"Completed (%)","scale":{"domain":[0,100],"zero":True}}}}
save("s07_regional_multiples",r)
save("s08_equity_lollipop",lolli("indexof(['First Nations','Not Indigenous','Low SES','Medium SES','High SES'],datum.group)>=0 && datum.cohort_start==2017",["First Nations","Not Indigenous","Low SES","Medium SES","High SES"],240))
k={**base(180),"data":{"url":G},"transform":[{"filter":"datum.section=='Mode of Attendance' && datum.cohort_start==2017 && datum.group!='Multi-modal'"},
 {"fold":["completed","still_enrolled","dropped_out","never_returned"],"as":["key","value"]},
 {"calculate":"{'completed':'Completed','still_enrolled':'Still studying','dropped_out':'Dropped out','never_returned':'Never came back'}[datum.key]","as":"outcome"}],
 "mark":"bar","encoding":{"y":{"field":"group","type":"nominal","title":None,"sort":["Internal","External"]},
 "x":{"field":"value","type":"quantitative","title":"Share of students (%)","scale":{"domain":[0,100]}},
 "color":{"field":"outcome","type":"nominal","title":None,"sort":["Completed","Still studying","Dropped out","Never came back"],"scale":{"domain":["Completed","Still studying","Dropped out","Never came back"],"range":[BLUE,LB,"#fdae6b","#c26a1b"]},"legend":{"orient":"top"}},
 "order":{"field":"key","sort":"ascending"}}}
save("s09_mode_stacked",k)
h={**base(260),"data":{"url":G},"transform":[{"filter":"indexof(datum.section,'Australian Tertiary')==0 && datum.group!='ATAR not provided or not required'"}],
 "mark":{"type":"rect","stroke":"white"},"encoding":{"x":{"field":"cohort_start","type":"ordinal","title":"Year students started","axis":{"labelAngle":0,"labelOverlap":True}},
 "y":{"field":"group","type":"ordinal","title":"ATAR band","sort":["95-100","90-94","80-89","70-79","60-69","50-59","30-49"]},
 "color":{"field":"completed","type":"quantitative","title":"Completed (%)","scale":{"scheme":"blues","domain":[30,100]}},
 "tooltip":[{"field":"group","title":"ATAR"},{"field":"cohort_start","title":"Year"},{"field":"completed","title":"% completed"}]}}
save("s10_atar_heatmap",h)
