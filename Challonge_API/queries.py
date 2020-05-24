tournament_by_slug = '''
    query TournamentEvents($slug: String!){
        tournament(slug:$slug){
        	id
        	name
        	countryCode
        	addrState
            url(relative: false)
            startAt
        }
    },
        '''