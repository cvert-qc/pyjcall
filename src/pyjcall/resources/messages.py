from typing import Dict, Any, Optional
from ..models.messages import ListMessagesParams, SendMessageParams, CheckReplyParams, SendNewMessageParams

class Messages:
    def __init__(self, client):
        self.client = client

    async def list(
        self,
        from_datetime: Optional[str] = None,
        to_datetime: Optional[str] = None,
        last_sms_id_fetched: Optional[int] = None,
        contact_number: Optional[str] = None,
        justcall_number: Optional[str] = None,
        sms_direction: Optional[str] = None,
        sms_content: Optional[str] = None,
        page: Optional[int] = None,
        per_page: Optional[int] = 20,
        sort: str = "id",
        order: str = "desc"
    ) -> Dict[str, Any]:
        """
        List SMS messages with optional filtering parameters.
        
        Args:
            from_datetime: Start datetime (yyyy-mm-dd hh:mm:ss or yyyy-mm-dd)
            to_datetime: End datetime (yyyy-mm-dd hh:mm:ss or yyyy-mm-dd)
            last_sms_id_fetched: ID of last SMS fetched in previous query
            contact_number: Contact number in E.164 format
            justcall_number: JustCall number in E.164 format
            sms_direction: Direction of SMS (Incoming/Outgoing)
            sms_content: Keywords in SMS content
            page: Page number
            per_page: SMS per page (max: 100)
            sort: Field to sort by
            order: Sort order (asc/desc)
            
        Returns:
            Dict[str, Any]: Paginated list of SMS messages
        """
        params = ListMessagesParams(
            from_datetime=from_datetime,
            to_datetime=to_datetime,
            last_sms_id_fetched=last_sms_id_fetched,
            contact_number=contact_number,
            justcall_number=justcall_number,
            sms_direction=sms_direction,
            sms_content=sms_content,
            page=page,
            per_page=per_page,
            sort=sort,
            order=order
        )

        return await self.client._make_request(
            method="GET",
            endpoint="/v2.1/texts",
            params=params.model_dump(exclude_none=True)
        )

    async def send(
        self,
        to: str,
        from_number: str,
        body: str,
        media_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send an SMS message.
        
        Args:
            to: Recipient number in E.164 format
            from_number: Sender JustCall number in E.164 format
            body: SMS content
            media_url: URL of media to attach (optional)
            
        Returns:
            Dict[str, Any]: Details of the sent message
        """
        params = SendMessageParams(
            to=to,
            from_number=from_number,
            body=body,
            media_url=media_url
        )

        return await self.client._make_request(
            method="POST",
            endpoint="/v2.1/texts",
            json=params.model_dump(exclude_none=True)
        )

    async def get(self, message_id: int) -> Dict[str, Any]:
        """
        Get details of a specific SMS message by ID.
        
        Args:
            message_id: Unique ID of the SMS message
            
        Returns:
            Dict[str, Any]: SMS message details
        """
        return await self.client._make_request(
            method="GET",
            endpoint=f"/v2.1/texts/{message_id}"
        )

    async def check_reply(
        self,
        contact_number: str,
        justcall_number: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Check for SMS replies from a specific contact.
        
        Args:
            contact_number: Contact number in E.164 format
            justcall_number: JustCall number in E.164 format (optional)
            
        Returns:
            Dict[str, Any]: Reply information
        """
        params = CheckReplyParams(
            contact_number=contact_number,
            justcall_number=justcall_number
        )

        return await self.client._make_request(
            method="POST",
            endpoint="/v2.1/texts/checkreply",
            json=params.model_dump(exclude_none=True)
        )

    async def send_new(
        self,
        justcall_number: str,
        contact_number: str,
        body: str,
        media_url: Optional[str] = None,
        restrict_once: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send a new SMS message.
        
        Args:
            justcall_number: JustCall number in E.164 format
            contact_number: Recipient number in E.164 format
            body: SMS content (max 1600 characters)
            media_url: Comma-separated URLs of media to attach (max 5)
            restrict_once: Set to 'Yes' to prevent duplicate SMS in 24 hours
            
        Returns:
            Dict[str, Any]: Details of the sent message
        """
        params = SendNewMessageParams(
            justcall_number=justcall_number,
            contact_number=contact_number,
            body=body,
            media_url=media_url,
            restrict_once=restrict_once
        )

        return await self.client._make_request(
            method="POST",
            endpoint="/v2.1/texts/new",
            json=params.model_dump(exclude_none=True)
        )
