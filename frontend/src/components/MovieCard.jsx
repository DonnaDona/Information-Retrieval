import React from 'react';
import {Avatar, Box, Card, CardMedia, Chip, Stack, Typography} from "@mui/material";

export function MovieCard({title, release, description, image, rating, duration, genres, urls}) {
    const roundness = 4;
    return (
        <Card sx={{
            width: 600,
            height: 300,
            padding: 0,
            margin: 1.6,
            marginBottom: 4,
            borderRadius: roundness,
            boxShadow: 4,
            position: 'relative',
        }}>
            <Stack flexDirection="row">
                <CardMedia
                    component="img"
                    sx={{
                        width: 210,
                        height: 300,
                        borderRadius: roundness,
                        borderBottomRightRadius: 0,
                        borderTopRightRadius: 0
                    }}
                    image={image}
                    alt="poster"
                />
                <Stack padding={2} paddingBottom={1.8} sx={{overflow: 'hidden'}}>
                    <Typography variant="h5" component="h2">
                        {title}
                    </Typography>
                    <Typography color="primary" variant="body1" component="span"
                                sx={{marginTop: 1}}>{release} - {duration}</Typography>
                    <Typography variant="body1" component="div" sx={{marginTop: 2}}>
                        {description}
                    </Typography>

                    <Stack direction="row" spacing={2}
                           sx={{overflowX: 'auto', marginTop: 2, position: 'relative', zIndex: 1}}>
                        {genres.map((genre) => (
                            <Chip label={genre} key={genre} sx={{backgroundColor: "#f5f5f5"}}/>
                        ))}
                    </Stack>

                    <Stack alignItems="flex-end" direction="row" spacing={1}
                           sx={{flexGrow: 1, position: 'relative', zIndex: 1}}>
                        {urls.map((url) => (
                            <Chip avatar={<Avatar src={url.image}/>} variant="outlined" color="primary" component="a"
                                  label={url.name} clickable href={url.url} key={url} sx={{bgcolor: 'white'}}/>
                        ))}
                    </Stack>

                </Stack>

                <Box sx={{position: 'absolute', marginLeft: 2,}}>
                    <Chip label={
                        <Stack direction='row' alignItems="flex-end">
                            <Typography variant="h5" component="span" sx={{fontWeight: "bold"}}>{rating}</Typography>
                            <Typography variant="h6" component="span">/10</Typography>
                        </Stack>
                    } color="primary"
                          sx={{
                              marginTop: 2,
                              marginRight: 4,
                              fontSize: 20,
                              position: 'relative',
                              zIndex: 1,
                              boxShadow: 8
                          }}/>
                </Box>

                <CardMedia
                    component="img"
                    sx={{
                        display: rating < 5 || rating > 8 ? 'block' : 'none',
                        marginLeft: rating > 8 ? 58 : 58,
                        marginTop: rating > 8 ? 2 : 14,
                        width: rating > 8 ? 200 : 150,
                        height: rating > 8 ? 300 : 160,
                        opacity: 0.3,
                        position: 'absolute',
                        top: 0,
                        left: 0,
                        zIndex: 0,
                    }}
                    image={rating > 8 ? "../../public/fire.png" : rating > 5 ? null : "../../public/fishy.png"}
                />

            </Stack>
        </Card>
    )
}
