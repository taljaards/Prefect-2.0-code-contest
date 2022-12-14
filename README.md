My entry to the Prefect 2.0 Code Contest launched just after Prefect 2.0's General Availability release.
<p align="center" style="margin-bottom:40px;">
<img src="https://i.imgur.com/L4oypPw.png"  height=440 style="max-height: 440px;">
</p>

This flow combines two things I have a strange fondness of:
- Prefect flow run names
- Craiyon ("DALL·E mini") images

The flow takes the 5 latest flow run names and uses them as prompts for Craiyon.

Though not really identifying any Prefect edge cases, it's an example of using:
- Using native Python inside a flow
- Using Prefect's logger
- Mapping
- .submit()
- Interacting with PrefectFutures
- Interacting with the API
- Caching
- Task concurrency limits

---

Most outputs come out "normal", Craiyon cannot always figure out how to match the adjectives to the animals. Now and then surprises pop up, for example _classic scorpion_:

<p align="center" style="margin-bottom:40px;">
<img src="https://i.lensdump.com/i/t5ndFx.png"  height=440 style="max-height: 440px;">
</p>

More examples are available here: https://lensdump.com/a/1FZ4C
