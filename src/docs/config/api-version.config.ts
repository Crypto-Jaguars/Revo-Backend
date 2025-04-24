import { ApiVersion } from '../interfaces/documentation.interface';

export const API_VERSIONS: ApiVersion[] = [
    {
        version: 'v1',
        status: 'active',
    },
    {
        version: 'v2',
        status: 'active',
    },
];

export const DEFAULT_VERSION = 'v1';

export const VERSION_HEADER = 'X-API-Version';

export const getApiVersion = (version: string): ApiVersion | undefined => {
    return API_VERSIONS.find((v) => v.version === version);
};

export const isVersionActive = (version: string): boolean => {
    const apiVersion = getApiVersion(version);
    return apiVersion?.status === 'active';
};

export const isVersionDeprecated = (version: string): boolean => {
    const apiVersion = getApiVersion(version);
    return apiVersion?.status === 'deprecated';
};

export const isVersionSunset = (version: string): boolean => {
    const apiVersion = getApiVersion(version);
    return apiVersion?.status === 'sunset';
}; 