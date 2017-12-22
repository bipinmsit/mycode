import os

class GraphQlObject:

    def session_aoi_query(ancestor):
        siteId = str(ancestor['Site'])
        stageId = str(ancestor['Stage'])
        sessionId = str(ancestor['Session'])

        query = '''
                    {
                        site(id: "''' + siteId + '''"){
                            id
                            name
                            clientId
                            clientName
                            stage(id: "''' + stageId + '''" ){
                                id
                                name
                                createdAt
                                session(id: "''' + sessionId + '''" ){
                                    id
                                    name
                                    artifacts{
                                        id
                                        name
                                        fileName
                                        fileCheckSum
                                        type
                                    }
                                }
                                aois{
                                    id
                                    name
                                    mergeReference
                                    artifacts{
                                        id
                                        name
                                        fileName
                                        type
                                        fileCheckSum
                                    }
                                }
                            }

                        }
                    }         
                    '''
        return query

    def download_file_query(file_name):
        query = '''
            {
              download(name: "''' + file_name + '''") {
                name
                type
                createdAt
                modifiedAt
                fileUrl
                fileType
              }
            }
            '''
        return query
