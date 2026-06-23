# Emergence Capital - AI-native services playbook

Titulo extraido: The AI-Native Services Playbook | Emergence Capital
URL: https://www.emcap.com/thoughts/the-ai-native-services-playbook
Categoria: case_materials
Tipo: case_material
Formato: article
Prioridade: high
Coletado em: 2026-06-23T03:11:28.087614+00:00

## Conteudo extraido

The AI-Native Services Playbook

At Emergence, we believe AI-Native Services will be a defining business model of the AI era (read why here ). But there's no playbook for it yet. The idea of selling a service powered primarily by AI wasn't possible until 2023. Founders building in this space are figuring out foundational elements of this new business model as they go.

We aim to be the most diligent students of this emerging business model. We're working with the early pioneers of the category, both within and outside our portfolio, to document the lessons on how to build. Many of these lessons look quite different than how to build a successful software company. Some are counterintuitive. All of them are still evolving.

This playbook is for founders and operators building (or considering) AI-native services companies. We'll update it every six months to capture the latest in how to build in AINS. If you're building here and have lessons to share, we want to hear from you.

I. Team

Domain expertise is a must have. In traditional SaaS, you're selling a product. In AI-native services, you're selling yourself. Domain credibility isn't just important; it's existential.

Early customers need to believe in your ability to deliver results, and established credibility goes a long way towards building that trust. They evaluate services by the reputation or perceived credibility and expertise of the person/people providing it. Past performance is a reliable predictor of future performance.

Industry experience is especially helpful in customer-facing team members; so much of this is about trust. You want the buyer to recognize the places your team has worked, ideally trusted brands from legacy service providers.

This domain expertise doesn't have to come from the co-founders; it can emerge as you build the team in the early days.

Mechanical Orchard: CEO Rob Mee (who previously ran Pivotal) brought instant credibility with enterprise buyers plus access to the Pivotal Labs talent network.

Harper and Pace: Both Dakotah Rice (Harper) and Jamie Cuffe (Pace) grew up in insurance families, giving them authentic domain credibility from day one. Harper's co-founder Tushar Nair brought the engineering depth; together they've served over 5,000 businesses in 13 months.

Hanover Park: Hired senior people from Standish and other established players in fund administration, which helped legitimize their offering while they built their AI-native approach from the ground up.

Crosby Legal : CEO Ryan Daniels was a top rising lawyer at a leading firm focused on the same practice areas Crosby is.

Domain authority also unlocks access to high-quality talent channels, which enables the rapid staffing you may need while your AI is still maturing.

Hire a product leader earlier than you think. Many AINS founders delay hiring a product leader since the customer rarely interacts with the software directly. This is a mistake. The complexity of AINS businesses requires a strong bridge between engineering and deployment. Without it, the product roadmap gets driven by whoever is shouting loudest rather than by a deliberate strategy for productization.

Your sales process must include someone who has a deep understanding of the service to be delivered. An AINS failure mode we've seen is where a seller who isn't intimately familiar with delivery overpromises on timelines, putting the delivery team in a bind. Involving a sales engineer or other technical resource ensures the complexity of the deployment is fully understood, and the engagement is scoped to succeed.

II. Product-Market Fit

Beware Mirage PMF. PMF is a different beast in AI-native services. Strong revenue growth and net dollar retention can mask a lack of true AI enablement.

Unlike SaaS, revenue growth and strong logo retention don't prove product-market fit. You only truly have it when AI is doing a material share of the work at a high gross margin and delivering superior customer outcomes. Otherwise, you've built a good services firm financed with the wrong kind of capital.

Real PMF requires proving you can scale non-linearly relative to your costs. To get there, your AI must drive measurable improvements in cost, quality, or speed, or ideally, all three.

How do you know if you have Mirage PMF? Watch for these early warning signs:

Gross margin is flat or declining even as revenue grows. If AI were doing more of the work, margins should be expanding. Be honest about what's in COGS: inference costs, model API spend, and human-in-the-loop labor all belong there. Too many founders offload labor costs to operating expenses, but since this is a service, they are absolutely COGS.

Revenue per employee (ARR/FTE) isn't improving. This is the simplest test of whether AI is pulling its weight. More granularly, you could isolate service-relevant FTEs to understand AI leverage over time.

Delivery is still human-heavy. If your team is growing linearly with your customer base, you're scaling like a traditional services firm.

Bespoke work is expanding. If each new customer requires significant custom engineering, you're not productizing.

You can't point to a north star product metric that's improving. Every AINS company needs a single number that captures how much of the work AI is actually doing. We talk more about specific effective metrics we’ve seen in the Metrics section of this playbook.

Be sharp about your ICP. AINS founders need to be extremely precise about their ideal customer profile. It can be harder for services businesses than software businesses to unwind from the wrong client engagements. A mismatched enterprise customer can consume enormous delivery resources, distract from productization, and create custom requirements that don't transfer to your broader customer base.

In some cases, it's actually easier for AINS businesses to productize by starting downmarket:

More homogeneity and fewer "out of the box" requests from smaller customers compared to the enterprise.

Lower ACVs force you to productize because you can't afford to throw human labor at each engagement.

Simpler, more standardized workflows mean fewer edge cases for your AI to handle, which means you can demonstrate real AI leverage faster.

Harper's focus on Main Street businesses (daycares, manufacturers, restaurants) rather than Fortune 500 accounts is a deliberate choice that illustrates all three of these dynamics.

But focusing downmarket doesn’t always correlate with easier productization in AINS. In some cases, larger enterprises may have more developed practices and repeatable requests. The most important thing is to be sharp about which ICP you’re focused on and why.

Focus on one or two jobs to be done. The more jobs you take on, the harder it becomes to productize your AI. Every new workflow requires new training data, new edge cases, new human oversight. Premature breadth is one of the fastest paths to Mirage PMF. You can always expand later. Strala exemplifies this discipline: they're focused specifically on claims processing for insurance carriers, captives, and MGAs. That narrow focus lets them build deep automation for a repeatable workflow.

III. Delivery

In SaaS, a customer buys your product and implements it. In AINS, you ARE the implementation. Delivery isn't a support function; it's the core of what you sell. That makes the practices around how you deliver, learn from delivery, and scale delivery the single most operationally important part of the business. Implementation/onboarding must be a core competency. Get this wrong and you'll scale headcount, not AI.

Staff pilots with a dedicated team. Have a specialized group that runs pilots so they become experts at managing extreme uncertainty, rather than having the pilot team roll on to the full project. The pilot team should be your SEAL team. The project team, which takes over after pilot success, should be better at integrating AI into steady-state delivery. Some continuity between the two is helpful, but the skill sets are different.

Sleep at your customer’s office. That may sound crazy, but the Hanover Park CEO makes this commitment (and follows through!) to ensure successful migration/implementation. The hardest part of AINS isn’t the AI; it’s the handoff from the legacy process. Over-invest in migration at a level that may seem absurd. It’ll pay off.

Sit doers next to builders. In AINS, the goal is to productize as much of the delivery process as possible over time. To do that, ensure you rotate people between product and delivery so learnings flow into the product. At Crosby Law, lawyers sit next to coders in pairs, creating real-time feedback between the people doing the work and the people building the AI. Crosby used to run evals in big batches, but switched to a model where lawyers give engineers feedback every few hours, allowing the engineers to tweak system prompts in real time. The system improved meaningfully after this switch.

That said, ensure the builders are given enough space to improve, not just replicate, existing processes. Domain experts can be focused on rebuilding what currently exists. The product and eng team needs to take in that feedback but think first principles on what the new/better AI-enabled way should be.

Start every board meeting with customer health. There's so much nuance in delivery that surfacing and problem-solving around customer learnings is even more important in AINS than in software companies.

IV. Product Roadmap

Every AINS company faces the same fundamental tension: customers are paying you for delivery today, but the entire venture thesis depends on what you build for tomorrow. Your product roadmap is where that tension either gets resolved or destroys you. ‍ Navigate the important vs. urgent tradeoff. Customer demands are loud and immediate. Internal platform investments are quiet and compounding. The failure mode is to become a traditional services business by neglecting platform development while responding to urgent client requests.

You have to balance three forces: what customers want, what's best for productization of your services, and how hard the product element is to build. The founders who get this right learn to say no to customer requests that don't map to their productization roadmap, even when the revenue is tempting. The best AINS companies find ways to prioritize the important work: they automate, they productize, and their margins expand. Those that fall prey to the urgent don't automate and don't find margin expansion.

Automate tasks, not people. This is a humbling realization for techie founders who want to fully eliminate a role. Think on a task basis instead. People can do more tasks when AI handles the repetitive ones. This framing is both more realistic and more palatable to customers nervous about AI replacing their teams. Thinking on a task basis also is the best way to build evals, which leads to faster productization.

Set a north star product metric that tracks the impact of AI improvements on service delivery across cost, speed, and/or quality. The specific metric will vary by business, but every AINS company needs one. Over time, product investments need to tie to measurable improvements in gross margin.

V. Go-to-Market

It's the demo, stupid! In SaaS, demos showcase product value. In AI-native services, the art of the demo has been forgotten. Founders default to pitch decks and talk tracks. This is understandable since the AI product isn't used directly by the customer; the service provider wields the magic internally to deliver outcomes.

But it's a huge mistake. Without a demo, it can be hard for a buyer to visualize what makes you different from every other service provider with a similar pitch. And if you're a startup competing with established, trusted services brands, it's even more critical to showcase your magic. Don't hide it behind the curtain.

We've seen AI-native services companies halve their sales cycles just by adding a demo. Mechanical Orchard started demoing the power of their product, which is effectively Cursor for COBOL, and saw sales cycles cut by more than half. The customer will never directly use this system. But seeing the AI in action converts skeptics into believers far faster than any slide deck. So stop telling prospects about your AI. Show 'em.

Develop partnerships early; they can be a key growth accelerator. Partnerships with incumbents can be a major accelerant for AINS. Incumbents offer immediate market credibility, established distribution, and access to proprietary datasets, which can be crucial in the early days while your data corpus is small.

The partnership models that work go well beyond traditional revenue-share approaches. Some startups are exploring equity share relationships with incumbents. Others are acquiring existing service providers. Prosper AI's partnership with Firstsource (a leading revenue cycle services provider) provides immediate distribution and deal flow that would take years to build independently. There's also a growing trend of incumbents actively seeking AI-native partners because they can't build the capabilities themselves fast enough.

Tactical partnership lessons from our portfolio:

Find a mid-sized incumbent services provider that's incentivized to care and where you have real top-level influence. Deprioritize the biggest legacy incumbents initially; they'll move slowly, even though the relationship feels validating.

Ensure you maintain the end customer relationship. Don't get disintermediated. Losing the direct customer relationship means losing the data flywheel.

You'll need to train partners to do the heaviest-lift human tasks that your AI isn't currently able to do. This division of labor will change over time as your AI improves, which is exactly why maintaining the relationship matters.

VI. Pricing

The entire technology industry is moving toward outcomes-based pricing. Software companies are starting to explore it, but they face real challenges: attribution is hard (how much value did the software add vs. the human using it?), and the line between copilot and autopilot remains blurry.

AI-native services are uniquely well positioned. By definition, an AINS company is providing all of the value: the customer hires you to deliver an outcome, and you're accountable for getting it done. There is no attribution problem. The service IS the outcome. This makes AINS the most natural home for outcome-based pricing in the entire AI economy.

How to structure outcome-based pricing in practice depends on the nature of the work:

Discrete, large-scope work: If each engagement is a well-defined project (e.g., migrating a mainframe, processing a complex insurance claim), you can price the specific piece of work directly. The outcome is clear, the scope is bounded, and the customer understands what they're paying for.

Continuous, variable work: If the work is ongoing and each task varies in complexity and value (e.g., handling a stream of customer service requests, processing a flow of insurance submissions), a credits-based model can work well. Credits let you normalize across tasks of different sizes while still tying price to output rather than hours. The key is that the credit unit should map to something the customer intuitively understands as a unit of work.

The practical path: Many founders will need to start with the market norm (typically labor-based pricing) while they're learning to deliver efficiently. This is fine. But set a clear timeline to transition to outcome-based pricing as your AI matures and your delivery model stabilizes. The companies that stay on labor-based pricing too long end up cannibalizing their own growth as automation increases.

Embed recurring revenue where possible. Some AINS businesses operate in industries where multi-year contracts and long-term service are the natural norm. Hanover Park, as an AI-native fund administrator, benefits from this: fund admin relationships typically last years. If your business or industry doesn't have that built-in stickiness, you can still create it. Palantir did this effectively by delivering customized analyses for clients and then charging for the leave-behind software on a recurring basis.

VII. Defensibility and Moats

Build the data flywheel from day one. In SaaS, the product generates data as a byproduct. In AINS, the data generated by doing the work IS the product advantage. Every engagement should make your AI better, your delivery faster, and your outcomes more predictable. To that end, ensure your MSA/engagement letters give you the ability to use the data from your service to improve your service.

Harper illustrates this well. Every lead, call, email, and policy generates data that feeds their AI, improving matching between businesses and underwriters and driving higher conversion rates over time. This is the hallmark of a great AINS business: the work compounds into a durable advantage. If you're not building this flywheel from day one, you're just a services company that uses AI tools.

One underappreciated form of data leverage: AINS companies can use AI to optimally match a client with the best internal service provider suited to serve them, understanding style, expertise, capacity, and other factors. This matching improves with every engagement.

Brand is a powerful and underappreciated moat. AINS is fundamentally about selling outcomes, which requires the customer to extend a lot of trust. In professional services, brand has always mattered (it's why the Big 4 command premiums despite often delivering mediocre work). How can AI-native startups address the cold start problem with respect to brand? Early on, you need to borrow credibility , either by hiring respected service providers or partnering with branded incumbents. Over time, the higher quality/speed of your work should enable you to build your own brand reputation.

Scope and dep
