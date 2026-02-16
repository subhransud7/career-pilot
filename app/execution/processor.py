class LinkProcessor:
    def process_links(self, links: list[str], source_type: str, csv_date: str | None = None):
        raise NotImplementedError


class SequentialProcessor(LinkProcessor):
    def __init__(self, ingestion_service):
        self.ingestion_service = ingestion_service

    def process_links(self, links: list[str], source_type: str, csv_date: str | None = None):
        results = []
        for link in links:
            results.append(self.ingestion_service.process_single_link(link, source_type, csv_date))
        return results
