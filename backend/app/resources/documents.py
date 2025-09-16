# backend/app/resources/documents.py
from flask_restx import Namespace, Resource, fields

# namespace for documents
ns = Namespace('documents', description='Document management')

# example request model
document_input = ns.model('DocumentInput', {
    'title': fields.String(required=True, description="Document title"),
    'content': fields.String(required=True, description="Document content")
})

# example response model
document_output = ns.model('DocumentOutput', {
    'id': fields.Integer,
    'title': fields.String,
    'content': fields.String
})

# in-memory store (for testing only)
documents = []
doc_id = 1

@ns.route('/')
class DocumentList(Resource):
    @ns.expect(document_input)
    @ns.marshal_with(document_output)
    def post(self):
        """Create a new document (dummy)"""
        global doc_id
        data = ns.payload
        new_doc = {
            "id": doc_id,
            "title": data["title"],
            "content": data["content"]
        }
        documents.append(new_doc)
        doc_id += 1
        return new_doc

    @ns.marshal_list_with(document_output)
    def get(self):
        """Get all documents (dummy)"""
        return documents
