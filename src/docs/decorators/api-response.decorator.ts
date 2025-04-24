import { applyDecorators, Type } from '@nestjs/common';
import { ApiResponse as SwaggerResponse, ApiOperation } from '@nestjs/swagger';
import { BaseResponseDto, BaseErrorResponseDto } from '../interfaces/documentation.interface';

export interface ApiResponseOptions {
    status: number;
    description: string;
    type?: Type<any>;
    isArray?: boolean;
}

export const ApiResponse = (options: ApiResponseOptions) => {
    const { status, description, type, isArray = false } = options;

    const responseType = type
        ? isArray
            ? Array<typeof type>
            : type
        : status < 400
            ? BaseResponseDto
            : BaseErrorResponseDto;

    return applyDecorators(
        ApiOperation({ summary: description }),
        SwaggerResponse({
            status,
            description,
            type: responseType,
            isArray,
        }),
    );
};

export const ApiSuccessResponse = (type: Type<any>, description: string, isArray = false) => {
    return ApiResponse({
        status: 200,
        description,
        type,
        isArray,
    });
};

export const ApiCreatedResponse = (type: Type<any>, description: string) => {
    return ApiResponse({
        status: 201,
        description,
        type,
    });
};

export const ApiBadRequestResponse = (description: string = 'Bad Request') => {
    return ApiResponse({
        status: 400,
        description,
    });
};

export const ApiUnauthorizedResponse = (description: string = 'Unauthorized') => {
    return ApiResponse({
        status: 401,
        description,
    });
};

export const ApiForbiddenResponse = (description: string = 'Forbidden') => {
    return ApiResponse({
        status: 403,
        description,
    });
};

export const ApiNotFoundResponse = (description: string = 'Not Found') => {
    return ApiResponse({
        status: 404,
        description,
    });
};

export const ApiInternalServerErrorResponse = (description: string = 'Internal Server Error') => {
    return ApiResponse({
        status: 500,
        description,
    });
}; 