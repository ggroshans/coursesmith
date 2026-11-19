import json
P=json.load(open('output/prose.json'))
ent=P.get('entries',P)
R={
'nature-found-075':[("such as the 2004 Stockholm Convention on persistent organic pollutants","such as {{ref:nature-found-099}}, signed in 2004")],
'nature-found-079':[("poor waste management","poor handling of waste")],
'nature-found-088':[("land turning to desert","land drying out into barren country")],
'nature-found-092':[("the growth in biomass obtained","the growth in living material obtained")],
'nature-found-095':[("in an estuary aggregate","where a river meets the sea aggregate"),("contamination or overfishing","contamination or from taking too many fish")],
'nature-found-107':[("Soundscape ecology studies the","The study of soundscapes covers the")],
'nature-hist-027':[("Biomimetics copies natural models, as","Copying natural models is another route, as")],
'nature-mkt-154':[("some fossil fuel divestment","selling off some holdings in fossil fuel companies")],
'nature-nbs-246':[("to pursue food sovereignty","to pursue {{ref:nature-nbs-317}}")],
'nature-nbs-317':[("climate resilience grounds","grounds of coping with a changing climate")],
'nature-nbs-325':[("is a retention basin","is a {{ref:nature-nbs-172}}")],
'nature-nbs-333':[("bring coastal erosion and land loss","bring the wearing away of the coast and land loss")],
'nature-nbs-334':[("are phytoextraction, phytostabilization, phytovolatilization and phytofiltration","are {{ref:nature-nbs-335}}, {{ref:nature-nbs-336}}, {{ref:nature-nbs-338}} and phytofiltration")],
'nature-nbs-344':[("and conservation tillage at least 30%","and {{ref:nature-nbs-291}} at least 30%")],
'nature-pol-053':[("In phytoremediation, deep","In {{ref:nature-nbs-334}}, deep")],
'nature-pol-067':[("count as bioenergy, energy","count as {{ref:nature-res-258}}, energy")],
'nature-pol-103':[("Carbon pricing on shipping charges ships for the gases they emit.","Charging for emissions in shipping means charging ships for the gases they emit.")],
'nature-pol-112':[("Developing countries fear green protectionism: environmental goals used as cover for shielding domestic industry.","Developing countries fear that environmental goals will be used as cover for shielding domestic industry from foreign competition.")],
'nature-pol-113':[("causes thermal pollution","causes {{ref:nature-res-262}}")],
'nature-pol-155':[("adopted as the Federal Water Pollution Control Act Amendments of 1972","adopted in 1972 as amendments to the federal law on {{ref:nature-res-263}}")],
'nature-pol-159':[("agencies can designate 'critical habitat' zones","agencies can designate {{ref:nature-pol-310}} zones")],
'nature-pol-232':[("people's right to know about toxic","people's right to be informed about toxic")],
'nature-pol-265':[("it might disguise trade protectionism","it might disguise trade barriers meant to shield home industry")],
'nature-pol-290':[("ratification of the Kyoto Protocol","ratification of the {{ref:nature-clim-056}}")],
'nature-pol-295':[("led to the landfill tax and","led to the {{ref:nature-pol-117}} and"),("that the waste hierarchy prefers","that the {{ref:nature-eecon-022}} prefers")],
'nature-pol-296':[("left by pyrolysis or","left by heating material without oxygen or")],
'nature-pol-297':[("the snow and ice albedo effect","the snow and ice {{ref:nature-nbs-090}} effect")],
'nature-pol-299':[("funds a Superfund for abandoned sites","funds {{ref:nature-pol-176}} cleanups of abandoned sites"),("and incremental health risk","and some added health risk")],
'nature-pol-303':[("climate, energy security and ecosystems","climate, the security of energy supply and ecosystems")],
'nature-pol-309':[("Indirect land use change is the unintended extra carbon emissions from land-use change elsewhere, caused by cropland expanding to meet","The indirect form of {{ref:nature-res-108}} is the unintended extra carbon emissions from cropland expanding elsewhere to meet"),("included indirect land use change in the California Low-Carbon Fuel Standard","included these indirect effects in California's {{ref:nature-pol-165}}")],
'nature-pol-314':[("A carbon credit scheme gave","A {{ref:nature-mkt-081}} scheme gave"),("Clean Development Mechanism credits and subsidised flood insurance","{{ref:nature-mkt-104}} credits and subsidised insurance against flood damage")],
'nature-res-229':[("raise the real exchange rate","raise the currency's price-adjusted value against others")],
'nature-res-256':[("or individual fishing quota,","or {{ref:nature-res-018}},")],
'nature-res-257':[("Intensive farming raised yields","Farming pushed for maximum output per hectare raised yields")],
'nature-res-263':[("nature-based solutions or","{{ref:nature-nbs-220}} or")],
'nature-val-008':[("is the quality-adjusted life year","is the {{ref:nature-val-026}}")],
'nature-val-106':[("counting non-additional costs","counting costs that would have occurred anyway"),("Only additional costs count.","Only costs caused by the policy count."),("Additionality is contested","{{ref:nature-mkt-144}} is contested")],
'nature-val-107':[("labelling rules and zoning.","labelling rules and {{ref:nature-pol-177}}."),("concern over regulatory capture led","concern over {{ref:nature-pol-040}} led")],
'nature-val-112':[("energy and resource efficiency,","energy efficiency and {{ref:nature-eecon-191}},"),("It also draws on industrial symbiosis, product life-cycle assessment, and","It also draws on {{ref:nature-eecon-017}}, {{ref:nature-acct-050}} of products, and"),("meets the triple bottom line without","meets the {{ref:nature-acct-114}} without"),("Critics call it greenwashing that","Critics call it {{ref:nature-nbs-075}} that")],
'nature-val-114':[("it has the maximum entropy.","it has the maximum {{ref:nature-eecon-109}}.")],
}
out={}
for k,subs in R.items():
    e=ent[k]; t=e['text']
    for a,b in subs:
        assert a in t,(k,a); t=t.replace(a,b,1)
    out[k]={'title':e['title'],'text':t}
json.dump({'entries':out},open('work/write/fill.zzzterm4.json','w'),indent=1,ensure_ascii=False)
print(len(out))
