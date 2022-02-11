
class Sentiment:

    @staticmethod
    def zero_shot_classification(
        data, lang='en', fields=[
            'headline', 'summary'], canidate_labels=[
            'positive', 'negative', 'neutral']):
        from transformers import pipeline
        classifier = pipeline("zero-shot-classification", device=0)
        results = []
        for d in data:
            entry = {}
            for key, value in d.items():
                if key in fields:
                    res = classifier(value, canidate_labels)
                    comp = {a: b for a, b in zip(res['labels'], res['scores'])}
                    entry[f"zero-shot-{key}-results"] = comp
                else:
                    entry[key] = value
            results.append(entry)
        return results
