"""
GraphQL schema for Farmers Marketplace.
"""

from typing import Any

import strawberry
from strawberry.fastapi import GraphQLRouter
from strawberry.schema.schema import Schema

from app.graphql.resolvers.user_resolver import UserMutation, UserQuery
from app.graphql.resolvers.farmer_resolver import FarmerQuery, FarmerMutation


@strawberry.type
class Query(UserQuery, FarmerQuery):
    """Root GraphQL queries (User + Farmer)."""

    @strawberry.field
    def hello(self) -> str:
        return "Hello Farmers Marketplace! 🌾"


@strawberry.type
class Mutation(UserMutation, FarmerMutation):
    """Root GraphQL mutations (User + Farmer)."""

    @strawberry.field
    def placeholder(self) -> str:
        return "Placeholder mutation"


# Create the schema
schema = strawberry.Schema(query=Query, mutation=Mutation)

# Create GraphQL router for FastAPI
graphql_router: GraphQLRouter[Schema, Any] = GraphQLRouter(schema)
