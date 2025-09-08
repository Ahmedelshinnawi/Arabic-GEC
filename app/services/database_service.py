from datetime import datetime
from typing import List, Optional

from app.database import CORRECTIONS_TABLE, supabase
from app.models.schema import CorrectionCreate, CorrectionInDB
from logger import get_logger

logger = get_logger(__name__)


class DatabaseService:
    @staticmethod
    def create_correction(correction: CorrectionCreate) -> CorrectionInDB:

        try:
            result = (
                supabase.table(CORRECTIONS_TABLE)
                .insert(
                    {
                        "original_text": correction.original_text,
                        "corrected_text": correction.corrected_text,
                        "created_at": datetime.now().isoformat(),
                    }
                )
                .execute()
            )

            if result.data:
                return CorrectionInDB(**result.data[0])
            else:
                raise Exception(f"Error creating correction: {result.error}")
        except Exception as e:
            logger.error(f"Error creating correction: {e!s}")
            raise e

    @staticmethod
    def get_all_corrections() -> List[CorrectionInDB]:

        try:
            result = (
                supabase.table(CORRECTIONS_TABLE)
                .select("*")
                .order("created_at", desc=True)
                .execute()
            )
            return [CorrectionInDB(**correction) for correction in result.data]
        except Exception as e:
            logger.error(f"Error getting all corrections: {e!s}")
            raise e

    @staticmethod
    def get_correction_by_id(id: int) -> Optional[CorrectionInDB]:
        try:
            result = (
                supabase.table(CORRECTIONS_TABLE).select("*").eq("id", id).execute()
            )
            return CorrectionInDB(**result.data[0]) if result.data else None

        except Exception as e:
            logger.error(f"Error getting correction by id: {e!s}")
            return None

    @staticmethod
    def delete_correction(id: int) -> bool:

        try:
            result = supabase.table(CORRECTIONS_TABLE).delete().eq("id", id).execute()

            return len(result.data) > 0
        except Exception as e:
            logger.error(f"Error deleting correction: {e!s}")
            return False


database_service = DatabaseService()
