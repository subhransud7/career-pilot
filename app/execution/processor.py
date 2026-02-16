class LinkProcessor:
    async def process_links(self, links: list[str], source_type: str, csv_date: str | None = None):
        raise NotImplementedError


# class SequentialProcessor(LinkProcessor):
#     def __init__(self, ingestion_service):
#         self.ingestion_service = ingestion_service

#     async def process_links(self, links: list[str], source_type: str, csv_date: str | None = None):
#         results = []
#         for link in links:
#             results.append(await self.ingestion_service.process_single_link(link, source_type, csv_date))
#         return results
class SequentialProcessor(LinkProcessor):
    def __init__(self, ingestion_service):
        self.ingestion_service = ingestion_service

    async def process_links(
        self,
        links: list[str],
        source_type: str,
        csv_date: str | None = None
    ):
        results = []

        for link in links:
            try:
                result = await self.ingestion_service.process_single_link(
                    link,
                    source_type,
                    csv_date
                )
                results.append(result)

            except Exception as exc:
                # Log and continue
                print(f"[PROCESSOR ERROR] link={link} error={exc}")
                results.append({
                    "status": "failed",
                    "link": link,
                    "error": str(exc),
                })
                continue

        return results
