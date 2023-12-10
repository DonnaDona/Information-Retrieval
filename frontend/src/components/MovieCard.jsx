import React from 'react'
import {Card, CardMedia, Stack, Typography} from "@mui/material";

export function MovieCard({title, release, description, image, rating, duration}) {
    const roundness = 4;
    return (
        <Card sx={{width: 600, padding: 0, margin: 1.6, marginBottom: 4, borderRadius: roundness, boxShadow: 4}}>
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
                <Stack padding={4}>
                    <Typography variant="h4" component="h2">
                        {title}
                    </Typography>
                    <Typography variant="body1" component="h3" sx={{marginTop: 1}}>{release} - {duration}</Typography>
                    <Typography variant="body1" component="div" sx={{marginTop: 2}}>
                        {description}
                    </Typography>
                    <Typography variant="body1" component="div" sx={{marginTop: 2}}>
                        {rating}
                    </Typography>
                </Stack>

                {rating > 7.5 && (
                    <Stack padding={1}>
                        <img src='../../public/fire.png' alt="popcorn" width="30" height="40"/>
                    </Stack>
                )}

            </Stack>
        </Card>
    )
}